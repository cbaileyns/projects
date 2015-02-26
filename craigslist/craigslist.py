class Craigslist():
    '''Craigslist class accepts a url that parses the list of urls contained in the url which was initially passes'''
    def __init__(self, url):
        '''Holds the url'''
        self.url = url
        self.links = []
        self.last = None
        self.getLinks()
        self.getLast()
        
    def getLinks(self):
        '''appends a list of links to be scraped to self.links'''
        req = requests.get(self.url)
        html = BeautifulSoup(req.text)
        urls = html.find_all('a', class_="hdrlnk")
        for url in urls:
            lnk = url['href'].split("/")[3]
            if lnk == self.last:
                break
            else:
                self.links.append(lnk)
        'return [urls[i]['href'].split("/")[3] for i in range(len(urls))]
    
    def getLast(self):
        '''determines the last link to append. the craigslist feed will update, therefore we do not want to create
           double entries in the data'''
        self.last = self.links[0]
    
    def getData(self, newurl):
        link = self.url[:-1].split("/")
        link.pop(3)
        link = "/".join(link) + "/" + newurl
        req = requests.get(link)
        html = BeautifulSoup(req.text)
        text = html.find(id="postingbody").text
        initialpost = html.find(id="display-date").text
        price = html.find_all("span", class_="price")[0].text
        try:
            info = html.find_all("span", class_="housing")[0].text.split(" - ")
        except:
            info = ""
        try:
            bedrooms = info[0][-3:][0]
        except:
            bedrooms = ""
        try:
            sqft = info[1][:4]
        except:
            sqft = ""
        try:
            lat = html.find(id="map")["data-latitude"]
        except TypeError:
            lat = ""
        try:
            lon = html.find(id="map")["data-longitude"]
        except TypeError:
            lon = ""
        try:
            address = html.find_all("div", class_="mapaddress")[0].text
        except IndexError:
            address = ""
        return link, price, bedrooms, sqft, lat, lon, address, text, initialpost
    
    def scrapeData(self):
        linklist = self.getLinks()
        self.last = linklist[0]
        return [self.getData(linklist[i]) for i in range(10)]
