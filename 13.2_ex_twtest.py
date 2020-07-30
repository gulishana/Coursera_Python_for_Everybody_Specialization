import urllib.request, urllib.parse, urllib.error
from twurl import augment
import ssl

# https://apps.twitter.com/
# Create App and get the four strings, put them in hidden.py

print('* Calling Twitter...')
# 'augment' funtion comes from code: 'twurl.py'
url = augment('https://api.twitter.com/1.1/statuses/user_timeline.json',
              {'screen_name': 'drchuck', 'count': '2'})
              # the last part is just a Python dictionary
print(url)

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

connection = urllib.request.urlopen(url, context=ctx)
#contex = ctx, is to shut off the security checking for SSL cerificate
data = connection.read()
print(data) #this will print out ugly, since they are UTF-8 not Unicode
#print(data.decode()) #then you can print out in a readable way

print ('======================================')
headers = dict(connection.getheaders())
# urllib eats the headers, this is the way to get back headers
print(headers) #again, they are not pretty
