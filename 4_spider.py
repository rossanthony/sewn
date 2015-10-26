from lxml import html
import robotparser
import urlparse
from urlparse import urljoin
import requests
from collections import defaultdict
import sys
import logging

logging.basicConfig(level=logging.DEBUG)


class Spider(object):

    def __init__(self):
        #print(sys.argv[1])
        self.baseUrl = sys.argv[1]  # URL to be indexed, the starting point for the crawler
        self.level = 0  # Starting level, gets incremented each time a new page is crawled
        self.depth = 15 # Limit for number of pages deep the spider should crawl
        self.allowDupes = False # Toggles whether to record duplicate URLs per page

        # Data structures
        self.urlsVisited = defaultdict(list) # holds a list of the URLs visited in order
        self.pageLinks = defaultdict(list) # holds a list of the links 
        
        # Get the robots.txt
        self.robotParser = robotparser.RobotFileParser()
        self.robotParser.set_url(urlparse.urljoin(self.baseUrl, 'robots.txt'))
        self.robotParser.read()
        
        # Kick off the recursive crawling function
        self.crawlForLinks(self.baseUrl)
        
        # Log the result (for debugging during development only)
        logging.debug(self.urlsVisited)
        logging.debug(self.pageLinks)

        # self.saveCrawlerFile()
        # self.saveResultsFile()

    
    # Recursive crawling function
    def crawlForLinks(self, url):
        page = requests.get(url)
        tree = html.fromstring(page.text)
        anchors = tree.xpath('//a') # Get all anchors on the page
        self.level += 1
        self.urlsVisited[self.level].append(url)

        for link in anchors:
            if 'href' in link.attrib:
                # Add each 'unqiue' link on the current page being crawled into the dictionary
                if not self.pageAlreadyAdded(self.getAbsoluteUrl(link, url)) or self.allowDupes:
                    self.pageLinks[self.level].append(self.getAbsoluteUrl(link, url))
            # else:
            #     logging.debug(link)
            #     print " ^^ " + url + " must contain an anchor element without an href attribute!!"

        # Recursive back through the urls just found on this page and run crawls on those pages
        for url in self.pageLinks[self.level]:
            if self.isAllowedUrl(url) and self.level < self.depth:
                if self.urlAlreadyCrawled(url):
                    print url + " already checked"
                else:
                    self.crawlForLinks(url)
            else:
                print "Disallowed URL: %s %s\n" % (self.level, url)


    def crawl(self, urlToCrawl):
        self.crawlTxt += "<Visited " + urlToCrawl + ">\n"
        page = requests.get(urlToCrawl)
        tree = html.fromstring(page.text)
        #Get all anchors on the page
        anchors = tree.xpath('//a')
        for link in anchors:
            self.crawlTxt += "\t<Link " + self.getAbsoluteUrl(link, urlToCrawl) + ">\n"

        # Now loop through each URL and 
        # check that its not restricted in robots.txt or outside of the root path of the site
        # for link in anchors:
        #     print self.getAbsoluteUrl(link)


    def urlAlreadyCrawled(self, url):
        for k in self.urlsVisited:
            for v in self.urlsVisited[k]:
                if url in v:
                    return True
        return False


    def pageAlreadyAdded(self, url):
        for v in self.pageLinks[self.level]:
            if url in v:
                return True
        return False


    # This method converts URLs into absolute ones
    def getAbsoluteUrl(self, link, currentPageUrl):
        if link.attrib['href'][:4] == 'http':
            return link.attrib['href']
        elif link.attrib['href'][:6] == 'mailto':
            return link.attrib['href']
        elif link.attrib['href'][:2] == './':
            # print "URL JOIN 1:"
            # print urljoin(currentPageUrl, link.attrib['href'])
            return self.baseUrl + link.attrib['href'][2:]
        elif link.attrib['href'][:1] == '/':
            return self.baseUrl + link.attrib['href'][1:]
        elif link.attrib['href'][:2] == '..':
            print "URL JOIN:"
            print urljoin(currentPageUrl, link.attrib['href'])
            return urljoin(currentPageUrl, link.attrib['href'])
            # print urlparse(link.attrib['href'])
        else:
            return self.baseUrl + link.attrib['href']


    # This method converts URLs into relative ones
    def getRelativeUrl(self, link):
        if not link:
            return False
        elif link[:2] == '..':
            print "could not check robots.txt for:"
            print link
            return False
        elif link[:2] == './':
            return link[1:]
        elif link[:1] == '/':
            return link
        elif link.find(self.baseUrl) == 0:
            return link.replace(self.baseUrl, '/')
        else:
            return False


    def isAllowedUrl(self, link):
        # Check if the URL is within the base URL
        if link.find(self.baseUrl) == 0:
            # Check if the robots.txt allows crawling of this URL
            if self.getRelativeUrl(link):
                return self.robotParser.can_fetch("*", self.getRelativeUrl(link))
        return False


# <Visited URL1>
#     <Link URL1>
#     <Link URL2>
# <Visited URL2>
#     <Link URL1>
#     ... etc.

# Robots
# User-agent: *
# Disallow: /files/
# Disallow: /images/
# Disallow: /testpage.html
# Disallow: /private/

# Get the spider crawling...
Spider()