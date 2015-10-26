from lxml import html
import requests

page = requests.get('http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/testpage.html')
tree = html.fromstring(page.text)

#Get all anchors on the page
anchors = tree.xpath('//a')

for link in anchors:
    print '<a href="' + link.attrib['href'] + '">' + link.text_content() + '</a>'
