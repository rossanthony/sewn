from lxml import html

domTree = html.parse('http://www.dcs.bbk.ac.uk/~martin/sewn/ls3/testpage.html')
anchors = domTree.xpath('//a') # Returns an array of all anchors on the page

for link in anchors:
    print '<a href="' + link.attrib['href'] + '">' + link.text_content() + '</a>'