# A basic web crawler, which outputs two files:
#  - crawl.txt    Listing the urls for each page visited, and the links contained within
#  - results.txt  The number of links to visited pages per <Visited URL>
# 
# To run, first ensure you have Python installed, `python --version` will confirm this,
# then run: `python spider.py <seed_url> <depth> <inc_dupes>`
# params:
#    1. <seed_url>    The URL of the page where the crawler should start
#    2. <depth>       Max number of pages deep the crawler should be allow to crawl
#    3. <excl_dupes>  An optional flag to exclude duplicate links from the output 
#                     (to include all links, don't pass anything as the 3rd arg)
# E.g. 
#       python spider.py http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/ 15
#
# @author   Ross Anthony <rantho01@mail.bbk.ac.uk>
# @version  1.0
# @since    25 Oct 2015
#
# Vendor dependencies:

from lxml import html        # provides methods for performing HTTP get requests on a url and parses the HTML into a searchable dom tree object
import robotparser           # for parsing of robots.txt files
import urlparse              # lib for parsing urls
from urlparse import urljoin # allows conversion of relative urls into absolute ones 
from collections import defaultdict # dictionary data structures
import sys                   # required for getting arg's from the command line
import logging               # for outputting logs during development and for debugging purposes

logging.basicConfig(level=logging.DEBUG) # provides verbose debug output, useful during development


class Spider(object):

    def __init__(self):
        self.seedUrl = sys.argv[1]       # URL to be indexed, the starting point for the crawler
        self.maxDepth = int(sys.argv[2]) # Limit for number of pages deep the spider should crawl
        self.currentDepth = 0            # Starting level, gets incremented each time a new page is crawled
        self.allowDupes = True           # Toggles whether to record duplicate URLs per page
        
        # Cmd line override for allowDupes toggle
        if len(sys.argv) > 3: self.allowDupes = False

        # Data structures
        self.urlsVisited = defaultdict(list) # holds an ordered list of the URLs visited
        self.pageLinks = defaultdict(list)   # holds a list of the links in each page
        
        # Get the robots.txt
        self.robotParser = robotparser.RobotFileParser()
        self.robotParser.set_url(urlparse.urljoin(self.seedUrl, 'robots.txt'))
        self.robotParser.read()
        
        # Kick off the recursive crawling function
        self.crawlForLinks(self.seedUrl)
        
        # Log the result (for debugging during development only)
        # logging.debug(self.urlsVisited)
        # logging.debug(self.pageLinks)

        self.saveCrawlerFile()
        self.saveResultsFile()

    
    # Recursive crawling function
    def crawlForLinks(self, url):
        tree = html.parse(url)
        anchors = tree.xpath('//a') # Get all anchors on the page
        self.currentDepth += 1
        self.urlsVisited[self.currentDepth].append(url)

        for link in anchors:
            if 'href' in link.attrib:
                # Add each 'unqiue' link on the current page being crawled into the dictionary
                if not self.pageAlreadyAdded(self.getAbsoluteUrl(link, url)) or self.allowDupes:
                    self.pageLinks[self.currentDepth].append(self.getAbsoluteUrl(link, url))

        # Loop back through the urls just found on this page and run crawls on each in turn
        if self.currentDepth <= self.maxDepth:
            for url in self.pageLinks[self.currentDepth]:
                if self.isAllowedUrl(url) and not self.urlAlreadyCrawled(url):
                    self.crawlForLinks(url)
            #     else:
            #         print url + " already checked" 
            # else:
            #     print "Disallowed URL: %s %s\n" % (self.currentDepth, url)


    def urlAlreadyCrawled(self, url):
        for k in self.urlsVisited:
            for v in self.urlsVisited[k]:
                if url in v:
                    return True
        return False

    # Helper method which checks if a URL has already been visited
    # 
    # Returns: Bool
    #
    def pageAlreadyAdded(self, url):
        for v in self.pageLinks[self.currentDepth]:
            if url == v:
                return True
        return False


    # Convert a URL into absolute
    # 
    # Returns: String (url)
    #
    def getAbsoluteUrl(self, link, currentPageUrl):
        if link.attrib['href'][:4] == 'http':       # link starts with a protocol so must already be absolute
            return link.attrib['href']
        elif link.attrib['href'][:6] == 'mailto':   # email mailto link
            return link.attrib['href'] 
        else: # URL is either relative, or up at least one folder from current page
            return urljoin(currentPageUrl, link.attrib['href'])


    # Convert URL into a URI relative to the Seed URL
    # (used by the isAllowedUrl method)
    #
    # Returns: String (uri)
    #
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
        elif link.find(self.seedUrl) == 0:
            return link.replace(self.seedUrl, '/')
        else:
            return False


    # Consult the robots.txt to see if the given URL can be crawled
    #
    # Returns: Bool 
    #
    def isAllowedUrl(self, link):
        # Check if the URL is within the base URL
        if link.find(self.seedUrl) == 0:
            # Check if the robots.txt allows crawling of this URL
            if self.getRelativeUrl(link):
                return self.robotParser.can_fetch("*", self.getRelativeUrl(link))
        return False


    # Iterate over the Visited Urls and then all links on each page,
    # output as a file [crawl.txt] in the following format:
    #
    # <Visited URL1>
    #     <Link URL1>
    #     <Link URL2>
    # <Visited URL2>
    #     <Link URL1>
    #     ... etc.
    #
    def saveCrawlerFile(self):
        output = ''
        for visitedUrlKey in self.urlsVisited:
            for visitedUrl in self.urlsVisited[visitedUrlKey]:
                output += "<Visited " + visitedUrl + ">\n"
                for linkOnPage in self.pageLinks[visitedUrlKey]:
                    output += "\t<Link " + linkOnPage + ">\n"
        crawlerFile = open("crawl.txt", "w")
        crawlerFile.write(str(output))
        crawlerFile.close()
        return True


    # Iterate over the Visited Urls and count how many links it contains to other pages Visited,
    # output as a file [results.txt] in the following format:
    #
    # <Visited URL1>
    #       <No of links to Visited pages: X>
    # <Visited URL2>
    #       <No of links to Visited pages: Y>
    # ... etc. 
    #   
    def saveResultsFile(self):
        totalLinks = []
        output = ''
        for key in self.urlsVisited:
            for visitedUrl in self.urlsVisited[key]:
                output += "<Visited " + visitedUrl + ">\n"
                output += "\t<No of links to Visited pages: "
                output += str(self.getLinkCount(visitedUrl, key)) 
                output += ">\n"
        crawlerFile = open("results.txt", "w")
        crawlerFile.write(str(output))
        crawlerFile.close()
        return True

    # Loop through the links found on a given visited url 
    # and count the links it contains to other urls visited
    #
    # Returns: Int 
    #
    def getLinkCount(self, url, key):
        count = 0
        for link in self.pageLinks[key]:
            if self.isVisitedUrl(link):
                count += 1
        return count


    # Check if a given url has already been visited
    #
    # Returns: Bool
    #
    def isVisitedUrl(self, url):
        for key in self.urlsVisited:
            for visitedUrl in self.urlsVisited[key]:
                if visitedUrl == url: 
                    return True
        return False


# Set the spider crawling...
Spider()
