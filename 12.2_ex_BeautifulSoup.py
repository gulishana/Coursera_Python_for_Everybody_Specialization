# To run this, you can install BeautifulSoup
# https://pypi.python.org/pypi/beautifulsoup4

# Or download the file
# http://www.py4e.com/code3/bs4.zip
# and unzip it in the same directory as this file

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
# import BeautifulSoup from the folder 'bs4'
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# create a  variable 'ctx' for following steps

url = input('Enter - ')
html = urllib.request.urlopen(url, context=ctx).read()
# html = urllib.request.urlopen(url,context=ctx) returns us somthing we could
# -loop through line by line with a for loop
# .read() returns us the entire document at that web page
# in a single big string with new lines at the end of each line
# html now is not in Unicode, but probably UTF-8 string
soup = BeautifulSoup(html, 'html.parser')
# BeautifulSoup knows how to deal with both UTF-8 and Unicode strings
# BeautifulSoup read through and deal with all the nasty bits
# HTMLs are very flexible, hard to parse as normal strings
# BeautifulSoup does magic and get a clean 'soup'

# Retrieve all of the anchor tags
tags = soup('a')
# eg. on the web page shows HTML:
# <a href="http://www.dr-chuck.com/page2.htm"> Second Page <>
# Each web page could have many anchor tags
for tag in tags:
    print(tag.get('href', None))
# Pull out all the href in the anchor tags on that web page

# If not ignore SSL certificate errors as above, you would not be able to
# open the web page with a SSL certificate that not in Python's official list
# But after you open it, you still can not see the 'https://' because of SSL
