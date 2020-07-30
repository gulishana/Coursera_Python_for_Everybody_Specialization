import urllib.request, urllib.parse, urllib.error
# remember you need to put 4 keys in the hidden.py
import twurl
import json
import sqlite3
import ssl

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

conn = sqlite3.connect('friends.sqlite')
cur = conn.cursor()

# 'CREATE TABLE IF NOT EXISTS' means:
#(1)We want this to be a restartable process,data from 1st time will be stored.
#(2)And 2nd time it will not recreate the table, not losing old data.
cur.execute('''CREATE TABLE IF NOT EXISTS People
            (id INTEGER PRIMARY KEY, name TEXT UNIQUE, retrieved INTEGER)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Follows
            (from_id INTEGER, to_id INTEGER, UNIQUE(from_id, to_id))''')
            # 'from_id' to 'to_id', thus making a directional data
            # (from_id,to_id) is UNIQUE for combination, not unique single value

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    acct = input('Enter a Twitter account, or quit: ')
    if (acct == 'quit'): break
    if (len(acct) < 1):
        cur.execute('SELECT id, name FROM People WHERE retrieved = 0 LIMIT 1')
        try:
            (id, acct) = cur.fetchone()
            # this gives us a tupple from (id,name)
            # 'id' comes from the database
        except:
            print('No unretrieved Twitter accounts found')
            continue
    else:
        cur.execute('SELECT id FROM People WHERE name = ? LIMIT 1',
                    (acct, ))
        try:
            id = cur.fetchone()[0]
            # if the person is not in the talbe, this is gonna to fail
        except:
            cur.execute('''INSERT OR IGNORE INTO People
                        (name, retrieved) VALUES (?, 0)''', (acct, ))
            conn.commit()
            # we commit it so later SELECTs will see this,
            # otherwise the lateer SELECTs will not see the one we just INSERTed
            if cur.rowcount != 1: # see how many row we have affected
                print('Error inserting account:', acct)
                continue
            id = cur.lastrowid
            # Grab the last row of 'id', the PrimaryKey assigned by SQL
            # We did not insert the 'id' above, but we want to know the value,
            # cursor only have done the insert for (name,retrieved)
    # So one way or another, we are :
    #(1) either gonna know the ID of the user that was there before,
    #(2) or inserted one, and gonna know the PrimaryKey of the current user.

    url = twurl.augment(TWITTER_URL, {'screen_name': acct, 'count': '100'})
    # search for up to 100 frieds
    print('Retrieving account', acct)
    try:
        connection = urllib.request.urlopen(url, context=ctx)
    except Exception as err:
        print('Failed to Retrieve', err)
        ####### This is how to print out the ERROR messages
        break

    data = connection.read().decode()
    headers = dict(connection.getheaders())
    print('Remaining', headers['x-rate-limit-remaining'])

    try:
        js = json.loads(data)
        # in case JSON fail when the json is syntactically bad
    except:
        print('Unable to parse json')
        print(data)
        break
    # Debugging : print(json.dumps(js, indent=4))

    if 'users' not in js:
        print('Incorrect JSON received')
        print(json.dumps(js, indent=4))
        # To debugg what happed if the JSON syntax doesn't has 'users'
        continue

    cur.execute('UPDATE People SET retrieved=1 WHERE name = ?', (acct, ))
    # set 'retrieved' as one of our retrieved accounts

    countnew = 0
    countold = 0
    for u in js['users']:
        friend = u['screen_name']
        print(friend)
        cur.execute('SELECT id FROM People WHERE name = ? LIMIT 1',
                    (friend, ))
        # check if this friend is already in the database
        try:
            friend_id = cur.fetchone()[0]
            countold = countold + 1
            # if the friend is not there, fetchone() will blow up (=None)
            # if fail, then drop down to the 'except:' codes
        except:
            cur.execute('''INSERT OR IGNORE INTO People (name, retrieved)
                        VALUES (?, 0)''', (friend, ))
            # if the friend is not there, set the 'retrieved' to 0
            conn.commit()
            # 'cur.rowcount': how many rows were affected by last transaction
            if cur.rowcount != 1:
                print('Error inserting account:', friend)
                continue
            friend_id = cur.lastrowid
            #since we only inserted one row, 'lastrowid'=PrimaryKey of new row
            countnew = countnew + 1
        cur.execute('''INSERT OR IGNORE INTO Follows (from_id, to_id)
                    VALUES (?, ?)''', (id, friend_id))
        # 'from_id' & 'to_id' are 2 outward pointing ForeignKey
        # Thus we're inserting the connection from this person to that person
    print('New accounts=', countnew, ' revisited=', countold)
    print('Remaining', headers['x-rate-limit-remaining'])
    conn.commit()

cur.close()
