import urllib.request, urllib.parse, urllib.error
import json
# API service for this assignment:
serviceurl='http://py4e-data.dr-chuck.net/geojson?'

while True:
    address = input('\nEnter location (or press enter to quit):')
    if len(address) < 1 : break
    url = serviceurl + urllib.parse.urlencode({'address':address})
    print('\nRetrieving:',url)
    data = urllib.request.urlopen(url).read().decode()
    print('Retrieved:',len(data),'characters')
    try:
        js = json.loads(data)
    except:
        print('Invalid JSON Structure')
        js = None
    if not js or 'status' not in js or js['status']!='OK':
        print('====== Failure To Retrieve ======')
        print(data)
        continue
    #print(json.dumps(js,indent=4))
    ID = js['results'][0]['place_id']
    print('Place id:',ID)
