## A basic web crawler in Python

Outputs two files:
  - crawl.txt    A nested list of the urls for each page visited, and the links contained within each page
  - results.txt  The number of links to other visited pages found on each <Visited URL>
 
To run, first ensure you have Python installed, `python --version` will confirm this, then run... 
    
    python spider.py <seed_url> <incl_dupes> <depth>

Params:
    1. <seed_url>    The URL of the page where the crawler should start
    2. <incl_dupes>  [optional] Flag to include duplicate links from the output (default = exclude dupes)
    3. <depth>       [optional] Number of pages deep the crawler should be allow to crawl (max limit = 100)
                     
E.g. 
    
    python spider.py http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/ dupes 50

^ this will run the spider with 'http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/' as the seed URL, including duplicates, with a max depth of 50
       
    python spider.py http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/

^ this will do the same as above but exclude duplicate links (max depth will default to 100)