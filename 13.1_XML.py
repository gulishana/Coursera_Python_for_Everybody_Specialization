import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET

url = input('Enter URL:')
print('Retrieving:',url)
data = urllib.request.urlopen(url).read()

# xml = xml.decode()
# print (xml)
# decode into readable structure for printing
print('\nRetrieved:',len(data),'characters')

xml = ET.fromstring(data)
tags = xml.findall('.//comment')
# find all 'comment' tag trees in a list
# must use 'comments/comment', not 'comment' alone
# or use './/comment' to look through the entire tree of XML for any tag named 'comment'
# print(tags)
print('Count:',len(tags))
# number of 'comment' tags
sum = 0
for tag in tags:
    ct = tag.find('count').text
    sum = sum + int(ct)
print('Sum:',sum)
