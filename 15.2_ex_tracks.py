import xml.etree.ElementTree as ET # to parse XML data
import sqlite3

conn = sqlite3.connect('trackdb.sqlite') # database connection
cur = conn.cursor() # a database handle

# Make some Fresh Tables using executescript()
# Execute a script containing a series of SQL commands,
# which are separated by semicolons(";").
# The triple coded string ''' means one big long string
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name  TEXT UNIQUE);
CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title  TEXT UNIQUE);
CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    album_id  INTEGER,
    title TEXT UNIQUE,
    len INTEGER, rating INTEGER, count INTEGER);
''')

# Ask a file name for XML
fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = '15.2_Library.xml'

# Followings are samples of XML:
# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>
def lookup(d, key):
    found = False
    for child in d:
        if found : return child.text
        if child.tag == 'key' and child.text == key :
            found = True
    return None
# This Apple XML is weird because the key for an object is inside of the object
# We are gonna loop through all of the children in this outer dictionary,
# and find a child.tag that has a particular key.

stuff = ET.parse(fname) # parse the string 'fname' to XML object 'stuff'
all = stuff.findall('dict/dict/dict') # 'KEY/TAG/TAG'
# get all Tracks with a list of all its information
print('Dict count:', len(all)) # number of Tracks we got

for entry in all: # iterate through each Track
    if (lookup(entry, 'Track ID') is None): continue
    # continue if there is no 'Track ID'
    name = lookup(entry, 'Name')
    artist = lookup(entry, 'Artist')
    album = lookup(entry, 'Album')
    count = lookup(entry, 'Play Count')
    rating = lookup(entry, 'Rating')
    length = lookup(entry, 'Total Time')
    # 'lookup' is the function that we built above, not a built-in function
    if name is None or artist is None or album is None: continue
    print(name, artist, album, count, rating, length)

    # Insert Data into Relational Tables
    # Because we set 'name' as a UNIQUE Field above,
    # thus it will blow up if we try to insert the same artist twice.
    # 'INSERT OR IGNORE' means putting a new Row into the table,
    # unless there's already a Row with the same name in the table.
    cur.execute('''INSERT OR IGNORE INTO Artist (name)
        VALUES (?)''', ( artist, ) )
        # '?' is where the 'artist' value goes, the value we got above
        # (artist, ) we force to make a tuple by adding ","
    cur.execute('SELECT id FROM Artist WHERE name=?', (artist, ))
    # Search 'id', which is the auto-generated Primary Key
    artist_id = cur.fetchone()[0]
    # Fetch 'artist_id' as Foreign Key for Table 'Album'
    ### Whole 3 lines of codes are dealing with new or exsiting names

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id)
        VALUES (?,?)''', ( album, artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, len, rating, count)
        VALUES (?,?,?,?,?)''',
        ( name, album_id, length, rating, count ) )
    # 'INSERT OR REPLACE' means if the UNIQUE constraint would be violated,
    # then this truns into an UPDATE

    conn.commit()
