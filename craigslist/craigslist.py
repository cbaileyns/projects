class Craigslist():
    '''Craigslist class accepts a url that parses the list of urls contained in the url which was initially passes'''
    def __init__(self, url, last=None):
        '''Holds the url'''
        self.url = url
        self.last = last
    def getLinks(self):
        '''Returns list of ad id's which will be passed to a new class'''
        req = requests.get(self.url)
        html = BeautifulSoup(req.text)
        urls = html.find_all('a', class_="hdrlnk")
        return [urls[i]['href'].split("/")[3] for i in range(len(urls))]
    def getData(self, newurl):
        link = self.url[:-1] + "/" + newurl
        req = requests.get(link)
        html = BeautifulSoup(req.text)
        text = html.find(id="postingbody").text
        initialpost = html.find(id="display-date").text
        price = html.find_all("span", class_="price")[0].text
        info = html.find_all("span", class_="housing")[0].text.split(" - ")
        bedrooms = info[0][-3:][0]
        sqft = info[1][:4]
        lat = html.find(id="map")["data-latitude"]
        lon = html.find(id="map")["data-longitude"]
        address = html.find_all("div", class_="mapaddress")[0].text
        return price, bedrooms, sqdt, lat, lon, address, text, initiapost
