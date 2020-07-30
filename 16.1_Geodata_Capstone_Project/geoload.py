#  We're simulating or using the Google Places API to lool places up
# so that we can visualize them in the map

import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

api_key = False
# If you have a Google Places API key, enter it here
# eg. api_key = 'AIzaSy___IDByT70'

if api_key is False:
    serviceurl = "http://py4e-data.dr-chuck.net/geojson?"
    # A subset of the available data for this homework,
    # which you can just go to this URL from a browser.
    # This subset does not have rate limit as Google API.
else :
    serviceurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

# Additional detail for urllib
# http.client.HTTPConnection.debuglevel = 1

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

fh = open("where.data")
count = 0
for line in fh:
    if count > 200 :
        print('Retrieved 200 locations, restart to retrieve more')
        break
    # loop through the lines
    address = line.strip() # pull out the address
    print('')
    cur.execute("SELECT geodata FROM Locations WHERE address= ?",
        (memoryview( address.encode() ) , ) )

    try:
        data = cur.fetchone()[0]
        print("Found in database ",address)
        continue
        # if the 'geodata' is already in DB, print it out
    except:
        pass # means Do Not blow up

    parms = dict()
    parms["query"] = address
    if api_key is not False: parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)

    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))
    # print out how much data we've got
    count = count + 1

    try:
        js = json.loads(data)
    except:
        print(data)  # We print in case Unicode causes an error
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print('==== Failure To Retrieve ====')
        print(data)
        break

    cur.execute('''INSERT INTO Locations (address, geodata) VALUES ( ?, ? )''',
        ( memoryview(address.encode()), memoryview(data.encode()) ) )
    conn.commit()

    if count % 10 == 0 :
        print('Pausing for a bit...')
        time.sleep(5)
        # Pause 5s for every 10 parsed data

print("Run geodump.py to read the data from the database so you can vizualize it on a map.")

####### Press "Ctrl+C" in Linux or "Ctrl+Z" in Windows,
####### will blow up the running program.