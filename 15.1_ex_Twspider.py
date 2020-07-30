# These codes both talk to Twitter API and the database
# After we retrieve the data and remember the data
# so that no need to retrieve again

from urllib.request import urlopen
import urllib.error
import twurl
import json
import sqlite3  ## import SQLite3
import ssl

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

# connect to SQLite3
# and if 'spider.sqlite' does not exist, SQLite3 creates it
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor() # get a cursor in SQLite3

# create a table 'Twitter' if it doesn't exist
# start this over and over and not lose data
## This is a Spidering Process
## We want a restartable process where we use a Database
cur.execute('''
            CREATE TABLE IF NOT EXISTS Twitter
            (name TEXT, retrieved INTEGER, friends INTEGER)''')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    acct = input('Enter a Twitter account, or quit: ')
    if (acct == 'quit'): break # type 'quit' to quit
    if (len(acct) < 1): # if only press 'Enter':
        cur.execute('SELECT name FROM Twitter WHERE retrieved = 0 LIMIT 1')
        # read from the database an unretrieved Twitter person
        # and grab all that person's friends
        try:
            acct = cur.fetchone()[0] # 'fetch one get one'
            # 'fetchone' means get 1st row from the query result set
            # [0] means get the 1st column of that 1st row
        except:
            print('No unretrieved Twitter accounts found')
            continue

    url = twurl.augment(TWITTER_URL, {'screen_name': acct, 'count': '5'})
    print('Retrieving', url)
    connection = urlopen(url, context=ctx)
    data = connection.read().decode()
    headers = dict(connection.getheaders())

    print('Remaining', headers['x-rate-limit-remaining'])
    js = json.loads(data)
    # Debugging
    # print json.dumps(js, indent=4)

    cur.execute('UPDATE Twitter SET retrieved=1 WHERE name = ?', (acct, ))
    # update the DB and change the 'retrieved' from 0 to 1
    # this means we already retrieved it

    countnew = 0
    countold = 0
    for u in js['users']:
        friend = u['screen_name']
        print(friend)
        cur.execute('SELECT friends FROM Twitter WHERE name = ? LIMIT 1',
                    (friend, ))
        # select the friends from Twitter where the name is the friend person
        try:
            count = cur.fetchone()[0]
            cur.execute('UPDATE Twitter SET friends = ? WHERE name = ?',
                        (count+1, friend))
            countold = countold + 1
        except:
            cur.execute('''INSERT INTO Twitter (name, retrieved, friends)
                        VALUES (?, 0, 1)''', (friend, ))
            countnew = countnew + 1
    print('New accounts=', countnew, ' revisited=', countold)
    conn.commit()
    # commit the transaction to see the change in DB next time as well
cur.close() # close the connection
