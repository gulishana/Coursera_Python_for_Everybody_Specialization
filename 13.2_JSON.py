import urllib.request, urllib.parse, urllib.error
import json

url = input('Enter URL:')
print('Retrieving:',url)

data = urllib.request.urlopen(url).read().decode()
print('\nRetrieved:',len(data),'characters')

js = json.loads(data)
print('JSON Dictionary:',len(js),'key,value pairs')

print('\nCount:',len(js['comments']))
# number of items in the list: 'comments'
sum = 0
for item in js['comments']:
    ct = item['count']
    sum = sum + int(ct)
print('Sum:',sum)
