from lxml import html
import requests

# Get the robots.txt
robots = requests.get('http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/robots.txt')
print robots.text