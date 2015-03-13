import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from geopy.geocoders import Nominatim
import datetime

class Craigslist():
    '''Craigslist class accepts a url that parses the list of urls contained in the url which was initially passes'''
    def __init__(self, url, filename, mode, last=None):
        '''Holds the url'''
        self.file = filename
        self.url = url
        self.links = []
        self.last = last
        self.data = None
        self.frame = None
        self.count = 0
        self.listerrors = []
        self.pagerrors = []
        self.data = []
        self.initFrame()
        self.initLast()
        
    def getLinks(self):
        '''appends a list of links to be scraped to self.links'''
        found = False
        itz = -1
        self.links = []
        while found == False and itz < 21:
            itz += 1
            try:
                req = requests.get(self.url[:-1] + str(itz*100) + self.url[-1:])
                html = BeautifulSoup(req.text)
                urls = html.find_all('a', class_="hdrlnk")
                for url in urls:
                    lnk = url['href'].split("/")[3]
                    print lnk
                    if lnk == self.last:
                        found = True
                        break
                    else:
                        self.links.append(lnk)
            except:
                self.pagerrors.append(self.url[:-1] + str(itz*100) + self.url[-1:])
        if len(self.links) > 0:
            self.getLast()
    
    def initFrame(self):
        self.frame = pd.read_csv(self.file,index_col=False)
        self.frame = self.frame.drop_duplicates("url",inplace=False)    
    def initLast(self):
        if self.last == None:
            ix = self.frame[self.frame.posting == max(self.frame.posting)].index.tolist()[0]
            self.last = self.frame[self.frame.posting == max(self.frame.posting)].loc[ix,"url"].split("/")[-1]
    
    def getLast(self):
        '''determines the last link to append. the craigslist feed will update, therefore we do not want to create
           double entries in the data'''
        self.last = self.links[0]
    
    def getData(self, newurl):
        link = self.url[:-1].split("/")
        link.pop(3)
        link[4] = link[4][:3]
        link = "/".join(link) + "/" + newurl
        aprt = Listing(link)
        return aprt.get()
    
    def scrape(self):
        self.getLinks()
        if len(self.links) > 0:
            for i in range(len(self.links)):
                try:
                    self.data.append(self.getData(self.links[i]))
                except:
                    self.listerrors.append(self.links[i])
    
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
                
    def frameit(self,mode="a"):
        if len(self.data) == 0:
            pass
        else:
            cols = ['price', 'sqft', 'bed', 'baths', 'type', 'basement', 'date', 'lat', 'long', 'url', 'den', 'posting', 'text', 'title', 'mapattrs', 'laundry', 'AC', 'area', 'pcode']
            self.frame = pd.DataFrame(self.data,columns=cols)
            if mode=="a":
                pd.DataFrame.to_csv(self.frame,self.file, columns=cols,header=False,index=False, mode=mode)
            else:
                pd.DataFrame.to_csv(self.frame,self.file, columns=cols,header=True, mode=mode)
            self.data = []


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
        self.rbar = self.rbar()
        self.den = self.with_den()
        self.laundry = self.laundry()
        self.ac = self.ac()

    def title(self):
        #self.title = html.find_all("h2", class_="postingtitle")
        return self.html.find_all("h2", class_="postingtitle")

    def rbar(self):
        return datetime.datetime.strptime(self.html.find_all("time")[0].text,"%Y-%m-%d %I:%M%p")
    
    def text(self):    
        #self.text = html.find(id="postingbody").text
        try:
            return self.html.find(id="postingbody").text.encode('ascii','ignore')
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
    
    def with_den(self):
        try:
            re.search("(d|D)en", str(self.text)).group()
            return 1
        except:
            return 0
    
    def laundry(self):
        try:
            re.search("w/d", str(self.mapattrs)).group()
            return "unit"
        except:
            try:
                re.search("bldg", str(self.mapattrs)).group()
                return "bldg"
            except:
                try:
                    re.search("on site", str(self.mapattrs)).group()
                    return "on site"
                except:
                    return "none"

    def ac(self):
        try: 
            re.search("(A|a)/(C|c)", str(self.text)).group()
            return 1
        except:
            try:
                re.search("(C|c)entral ((A|a)|(H|h)eat)", str(self.text)).group()
                return 1
            except:
                return 0
                            
                                                            
    def get(self):
        return [self.price, self.sqft, self.bed, self.baths, self.type, self.basement, self.date, self.lat, self.long, self.url, self.den, self.rbar, self.text, self.title, self.mapattrs, self.laundry, self.ac]


t = Craigslist("http://toronto.craigslist.ca/search/tor/apa?s=&", "/Users/chrisbailey/Documents/toronto.csv","a")
t.scrape()
t.address()
t.frameit()
s = Craigslist("http://sfbay.craigslist.org/search/sfc/apa?s=&", "/Users/chrisbailey/Documents/sf.csv","a")
s.scrape()
s.address()
s.frameit()
