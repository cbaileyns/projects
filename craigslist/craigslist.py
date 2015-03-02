import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time
from pandasql import *
from geopy.geocoders import Nominatim

class Craigslist():
    '''Craigslist class accepts a url that parses the list of urls contained in the url which was initially passes'''
    def __init__(self, url, last=None, frame=None):
        '''Holds the url'''
        self.url = url
        self.links = []
        self.last = last
        self.data = []
        self.frame = frame
        self.count = 0
        
    def getLinks(self):
        '''appends a list of links to be scraped to self.links'''
        self.links = []
        req = requests.get(self.url)
        html = BeautifulSoup(req.text)
        urls = html.find_all('a', class_="hdrlnk")
        for url in urls:
            lnk = url['href'].split("/")[3]
            print lnk
            if lnk == self.last:
                break
            else:
                self.links.append(lnk)
        if len(self.links) > 0:
            self.getLast()
        #return [urls[i]['href'].split("/")[3] for i in range(len(urls))]
    
    def getLast(self):
        '''determines the last link to append. the craigslist feed will update, therefore we do not want to create
           double entries in the data'''
        self.last = self.links[0]
    
    def getData(self, newurl):
        link = self.url[:-1].split("/")
        link.pop(3)
        link = "/".join(link) + "/" + newurl
        aprt = Listing(link)
        return aprt.get()
    
    def scrape(self):
        self.getLinks()
        if len(self.links) > 0:
            for i in range(len(self.links)):
                self.data.append(self.getData(self.links[i]))             
    
    def address(self):
        for i in range(self.count, len(self.data)):
            self.count += 1
            try: 
                geolocator = Nominatim()
                location = geolocator.reverse((self.data[i][7],self.data[i][8])).address.split(",")
                area = location[-5]
                pcode = location[-2]
                self.data[i].append(area)
                self.data[i].append(pcode)
            except:
                self.data[i].append("")
                self.data[i].append("")
                
    def frameit(self):
        self.frame = pd.DataFrame(self.data)
        self.frame.columns = ["price", "sqft", "bed", "baths", "type", "basement", "date", "lat", "long", "url","area","pcode"]
        


class Listing():
    def __init__(self, url):
        self.url = url
        self.req = requests.get(self.url)
        self.html = BeautifulSoup(self.req.text)
        self.title = self.title()
        self.price = self.price()
        self.bed = self.bed()
        self.text = self.text()
        self.mapattrs = self.mapattrs()
        self.lat = self.lat()
        self.long = self.lon()
        self.type = self.type()
        self.basement = self.isBasement()
        self.baths = self.baths()
        self.date = self.date()
        self.sqft = self.sqft()

    def title(self):
        #self.title = html.find_all("h2", class_="postingtitle")
        return self.html.find_all("h2", class_="postingtitle")

    def text(self):    
        #self.text = html.find(id="postingbody").text
        try:
            return self.html.find(id="postingbody").text
        except:
            return ""
    
    def mapattrs(self):            
        #self.mapattrs = html.find_all("div", class_="mapAndAttrs")
        return self.html.find_all("div", class_="mapAndAttrs")
        
    def price(self):
        try:
            return re.search("\$\d+", str(self.title)).group()[1:]
        except:
            return ""
        
    def bed(self):
        try:
            return re.search("\d(br|BR)", str(self.title)).group()[0]
        except:
            return 1

    def sqft(self):
        try:
            return re.search("\d+(ft)", str(self.title)).group()[:-2]
        except:
            return ""
    
    def lat(self):
        try: 
            return re.search('[data-latitude="](-?\d+\.\d+)', str(self.mapattrs)).group()[1:]
        except:
            return ""
    
    def lon(self):
        try:
            return re.search("(-?\d+\.\d+)", re.search('(data-longitude=")(-?\d+\.\d+)', str(self.mapattrs)).group()).group()
        except:
            return ""
    
    def baths(self):
        try:
            return re.search("\d", re.search("\d</b>Ba",str(self.mapattrs)).group()).group()
        except:
            return ""
    
    def date(self):
        try:
            return re.search('\d+-\d+-\d+', str(self.mapattrs)).group()
        except:
            return ""

    def type(self):
        try:
            return re.search("condo|apartment", str(self.mapattrs)).group()
        except:
            try:
                return re.search("condo|apartment", str(self.text)).group()
            except:
                return ""

    def isBasement(self):
        try:
            re.search("(b|B)asement", str(self.title)).group()
            return 1
        except:
            try: 
                re.search("(b|B)asement (a|A)partment", str(self.text)).group()
                return 1
            except:
                return 0
                    
    def get(self):
        return [self.price, self.sqft, self.bed, self.baths, self.type, self.basement, self.date, self.lat, self.long, self.url]
