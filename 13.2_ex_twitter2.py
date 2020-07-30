import urllib.request, urllib.parse, urllib.error
import twurl
import json
import ssl

# https://apps.twitter.com/
# Create App and get the four strings, put them in hidden.py

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
# we are goint to look at someone's friends list

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    print('')
    acct = input('Enter Twitter Account:')
    # ask for the friends
    if (len(acct) < 1): break
    url = twurl.augment(TWITTER_URL,
                        {'screen_name': acct, 'count': '5'})
    #ask for the screen name, and the first 5 friends
    print('Retrieving', url)
    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()

    js = json.loads(data)
    print(json.dumps(js, indent=2)) # make a pretty print

    headers = dict(connection.getheaders())
    print('Remaining', headers['x-rate-limit-remaining'])

    # js is a dictionary, the outer is {}
    # js['users'] is a list (array) in the data structure
    for u in js['users']:
        print(u['screen_name'])
        if 'status' not in u:
            print('   * No status found')
            continue # break back to the beginning of the loop
        s = u['status']['text']
        print('  ', s[:50]) # print the first 50 characters of text
