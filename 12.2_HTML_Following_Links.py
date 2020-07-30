import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input('Enter URL: ')
count = input('Enter count: ')
ct = int(count)
position = input('Enter position: ')
ps = int(position)

while ct>0 :
    print('Retrieving:',url)
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')
    tag = tags[ps-1]
    # print('TAG:', tag)
    print('Name:', tag.contents)
    # get the text node between the tags
    url = tag.get('href', None)
    # get the content of the attribute 'href' which is the URL
    ct = ct - 1
