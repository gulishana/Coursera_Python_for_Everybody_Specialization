from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input('Enter URL: ')
html = urlopen(url, context=ctx).read()

soup = BeautifulSoup(html, "html.parser")

# Retrieve all of the anchor (<span>...</span>) tags
tags = soup('span')
count = 0
number = list()
for tag in tags:
    # print('TAG:', tag)
    num = tag.contents[0]
    # 'tag.contents' returns a list, we want the string 'tag.contents[0]'
    number.append(int(num))
    count = count + 1

print('Count:', count)
print('Sum:',sum(number))
