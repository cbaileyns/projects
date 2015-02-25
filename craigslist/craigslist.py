class Craigslist():
    '''Craigslist class accepts a url that parses the list of urls contained in the url which was initially passes'''
    def __init__(self, url):
        '''Holds the url'''
        self.url = url
        self.last = None
    def getLinks(self):
        '''Returns list of ad id's which will be passed to a new class'''
        req = requests.get(self.url)
        html = BeautifulSoup(req.text)
        urls = html.find_all('a', class_="hdrlnk")
        return [urls[i]['href'].split("/")[3] for i in range(len(urls))]
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
