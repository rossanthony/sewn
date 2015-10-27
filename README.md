## A basic web crawler in Python

Outputs two files:
 - crawl.txt    Listing the urls for each page visited, and the links contained within
 - results.txt  The number of links to visited pages per <Visited URL>

To run, first ensure you have Python installed, checking the output of `python --version` in your terminal will confirm this. Then run: `python spider.py <url_to_crawl> <depth>`, replacing the 2nd to last param with the starting
point for the crawler and the last param with how many pages deep you would like the crawler to go. For example:

    python spider.py http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/ 10