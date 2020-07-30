import urllib.request, urllib.parse, urllib.error
import json

# Note that Google is increasingly requiring keys
# for this Google Maps API
serviceurl = 'http://maps.googleapis.com/maps/api/geocode/json?'

while True:
    address = input('Enter location: ')
    if len(address) < 1: break
    # break out if only clicks 'Enter' without location

    url = serviceurl + urllib.parse.urlencode({'address': address})
    # http://maps.googleapis.com/maps/api/geocode/json?'address=...'
    print('Retrieving', url)
    uh = urllib.request.urlopen(url)
    data = uh.read().decode()
    # read data & decode into Unicode in Python
    print('Retrieved', len(data), 'characters')

    try:
        js = json.loads(data)
    except:
        js = None # None means no js, which means (not js) below

    if not js or 'status' not in js or js['status'] != 'OK':
        print('==== Failure To Retrieve ====')
        print(data)
        continue  # quit the program

    print(json.dumps(js, indent=4))
    # 'dumps()' is the opposite of 'loads()'
    # take the dictionary with arrays, then pretty print it with indent=4

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]
    print('lat', lat, 'lng', lng)
    location = js['results'][0]['formatted_address']
    print(location)
    # 'results' is a list, thus results[0] is the first element of the list
    # the rests are all dictionaries, thus only show the value name
