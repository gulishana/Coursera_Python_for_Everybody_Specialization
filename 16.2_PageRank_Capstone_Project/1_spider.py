import sqlite3
import ssl
import urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('spider.sqlite') # create database
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT,
     error INTEGER, old_rank REAL, new_rank REAL)''')
# PageRank: take the old rank and computes the new rank,
# then replaces the new rank with the old rank

cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER)''')
# a Many-to-Many table

cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Check to see if we are already in progress...
cur.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
# 'html is NULL' is the indicator that a page has not yet been retrieved
# 'ORDER BY RANDOM() LIMIT 1': just randomly pick a record in this database
row = cur.fetchone()
if row is not None:
    print("Restarting existing crawl.  Remove spider.sqlite to start a fresh crawl.")
else :
    starturl = input('Enter web url or enter: ')
    if ( len(starturl) < 1 ) : starturl = 'http://www.dr-chuck.com/'
    if ( starturl.endswith('/') ) : starturl = starturl[:-1]
    web = starturl
    if ( starturl.endswith('.htm') or starturl.endswith('.html') ) :
        pos = starturl.rfind('/')
        web = starturl[:pos]

    if ( len(web) > 1 ) :
        cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES (?)', ( web,))
        cur.execute('INSERT OR IGNORE INTO Pages (url,html,new_rank) VALUES (?,NULL,1.0 )', (starturl,))
        conn.commit()

# Get the current webs.
# This 'Webs' table is used to limit the links.
# It only does links to the sites that you tell it to do links,
# and probably best for the PageRank is to stick with one site.
# Otherwise, you'll never find the same site again if you let this wander the web aimlessly.
cur.execute('''SELECT url FROM Webs''')
webs = list()
for row in cur:
    webs.append(str(row[0]))
print(webs)

many = 0
while True:
    if ( many < 1 ) :
        sval = input('How many pages:')
        # Ask for how many pages we want to Spider
        if ( len(sval) < 1 ) : break
        #### Exit the program by press "Enter"
        many = int(sval)
    many = many - 1

    cur.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
    try:
        row = cur.fetchone()
        # print row
        fromid = row[0] # from_id is the page we're linking from
        url = row[1]
    except:
        print('No unretrieved HTML pages found')
        many = 0
        break

    print(fromid, url, end=' ')

    # If we are retrieving this page, there should be no links from it
    # To make sure we're gonna wipe out all of the links because it's unretrieved.
    # We're gonna wipe out from the links,
    # the links is the connection table that connects from pages back to pages.
    cur.execute('DELETE from Links WHERE from_id=?', (fromid, ))
    try:
        document = urlopen(url, context=ctx)
        # we're no decoding it since BeautifulSoup compensates for the UTF-8
        html = document.read()
        # This is the HTML error code, and we checked '200' is a Good Error
        if document.getcode() != 200 : # If we get a Bad Error:
            print("Error on page: ",document.getcode())
            # we're gonna say this error on page
            cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(),url))
            # we're gonnna set that error and update pages,
            # in which way we don't retrieve that page ever again.
        if 'text/html' != document.info().get_content_type() :
        # We check to see if the content type is Text/HTML (from HTTP contract)
        # We only want to look for the links on HTML pages,
        # so we wipe that guy out if we get a JPEG or something else.
            print("Ignore non text/html page")
            cur.execute('DELETE FROM Pages WHERE url=?', ( url,) )
            cur.execute('UPDATE Pages SET error=0 WHERE url=?', (url,) )
            conn.commit()
            continue
        print('('+str(len(html))+')', end=' ')
        # If the page is good,print out how many characters we've got
        soup = BeautifulSoup(html, "html.parser")
        # Then we parse the page we like.

    except KeyboardInterrupt:
    # 'KeyboardInterrupt' is what happens when we press 'Ctrl+Z' on Windows
        print('')
        print('Program interrupted by user...')
        break
    except:
    # Some other exceptions probably means BeautifulSoup or something else blew up
        print("Unable to retrieve or parse page")
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
        # we indicate with 'error=-1' for that URL so we don't retrieve it again
        conn.commit()
        continue

    # At this point, we've got the HTML for thar URL, so we're gonna to insert it in,
    # and we're gonna set the PageRank to 1.
    # How PageRank works is it gives all the pages some normal value then it alters that.
    cur.execute('INSERT OR IGNORE INTO Pages (url,html,new_rank) VALUES (?, NULL,1.0)', (url,))
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (memoryview(html),url) )
    conn.commit()

    # Retrieve all of the anchor tags by BeautifulSoup
    tags = soup('a')
    count = 0
    for tag in tags:
        href = tag.get('href', None)
        if ( href is None ) : continue

        # Resolve relative references like href="/contact"
        # Below are all relative references by taking the current URL and looking it up.
        up = urlparse(href)  # 'urlparse' gonna break the URL into pieces
        if ( len(up.scheme)<1 ) : href = urljoin(url, href)
        # Scheme of URL is HTTP or HTTPS
        # 'urljoin' knows aboat slashes('/') and all those other things
        ipos = href.find('#')
        # Check to see if there's an anchor, the pound('#') sign at the end of URL
        if ( ipos > 1 ) : href = href[:ipos]
        # Throw everything past, including the anchor away
        if ( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif')):
            continue
        # If we have a JPEG or PNG or GIF, we're gonna skip it.
        if ( href.endswith('/') ) : href = href[:-1]
        # if we have '/' at the end, we're gonna chop the '/' by saying '-1'
        if ( len(href) < 1 ) : continue
        # Above are all nasty choppage and throwing away the URLs that
        # that have something we don't like, or we have to clean them up or ...
        # So now it's an absolute URL, clean

		# Check if the URL is in any of the webs
        # Check through all the 'webs', which is the URLs that we're willing to stay with
        # If this would link off the sites we're interested in, we'll skip it.
        # W're not interested in the links that will leave the sites.
        found = False
        for web in webs:
            if ( href.startswith(web) ) :
                found = True
                break
        if not found : continue

        # So now we've got the good lind we want, then add it into database
        cur.execute('INSERT OR IGNORE INTO Pages (url,html,new_rank) VALUES (?,NULL,1.0 )', (href,))
        count = count + 1
        conn.commit()

        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', (href,))
        # Get the 'id' that either was alreday there or was just created:
        try:
            row = cur.fetchone() # grab the 'id'
            toid = row[0] # set the value of to_id, which is the page we're linking to
        except:
            print('Could not retrieve id')
            continue

        cur.execute('INSERT OR IGNORE INTO Links (from_id,to_id) VALUES (?,?)', (fromid,toid))

    print(count)

cur.close()
