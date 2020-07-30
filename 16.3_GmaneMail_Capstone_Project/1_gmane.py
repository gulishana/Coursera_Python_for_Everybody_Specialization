# This spidering process may take a few days to finish.
import sqlite3
import time
import ssl
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
import re  # To use Regular Expression for parsing email
from datetime import datetime, timedelta
# This is a datetime parsing.
# There's code that's out there but you may have to install it.
# So here Dr. Chuck wrote a code for us.

# Not all systems have this so conditionally define parser
try:
    import dateutil.parser as parser
except:
    pass

def parsemaildate(md) :
    # See if we have dateutil
    try:
        pdate = parser.parse(tdate)
        test_at = pdate.isoformat()
        return test_at
    except:
        pass

    # Non-dateutil version - we try our best

    pieces = md.split()
    notz = " ".join(pieces[:4]).strip()

    # Try a bunch of format variations - strptime() is *lame*
    dnotz = None
    for form in [ '%d %b %Y %H:%M:%S', '%d %b %Y %H:%M:%S',
        '%d %b %Y %H:%M', '%d %b %Y %H:%M', '%d %b %y %H:%M:%S',
        '%d %b %y %H:%M:%S', '%d %b %y %H:%M', '%d %b %y %H:%M' ] :
        try:
            dnotz = datetime.strptime(notz, form)
            break
        except:
            continue

    if dnotz is None :
        # print 'Bad Date:',md
        return None

    iso = dnotz.isoformat()

    tz = "+0000"
    try:
        tz = pieces[4]
        ival = int(tz) # Only want numeric timezone values
        if tz == '-0000' : tz = '+0000'
        tzh = tz[:3]
        tzm = tz[3:]
        tz = tzh+":"+tzm
    except:
        pass

    return iso+tz

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

baseurl = "http://mbox.dr-chuck.net/sakai.devel/"
# A copy of the data from Gmain Server API, which is much quicker to spider

cur.execute('''CREATE TABLE IF NOT EXISTS Messages
    (id INTEGER UNIQUE, email TEXT, sent_at TEXT,
     subject TEXT, headers TEXT, body TEXT)''')
# Create a simple table

# Pick up where we left off
start = None
cur.execute('SELECT max(id) FROM Messages' )
# Select the largest PrimaryKey from the 'Messages' Table and retrieve that.
try:
    row = cur.fetchone() # Then go to the one after that
    if row is None :
        start = 0
    else:
        start = row[0]
except:
    start = 0

if start is None : start = 0
# We have a starting point, that starts with 0 or 1.

many = 0
count = 0
fail = 0
while True:
    if ( many < 1 ) :
        conn.commit()
        sval = input('How many messages:')
        # Ask for how many messages to retrieve.
        if ( len(sval) < 1 ) : break
        # Press "Enter" to quit the program.
        many = int(sval)

    start = start + 1
    cur.execute('SELECT id FROM Messages WHERE id=?', (start,) )
    try:
        row = cur.fetchone()
        if row is not None : continue
        # Not None: means we've already retrieved this particular email message
    except:
        row = None
        # None: we've not retrieved this one yet, good to start retrieving.

    many = many - 1
    url = baseurl + str(start) + '/' + str(start + 1)
    # take the base URL and add the starting address and then add +1

    text = "None"
    try:
        # Open with a timeout of 30 seconds
        document = urllib.request.urlopen(url, None, 30, context=ctx)
        text = document.read().decode()
        if document.getcode() != 200 :
        # Check to see if we got legit data
        # eg. "404: Not Found" , we're gonna quit
            print("Error code=",document.getcode(), url)
            break
    except KeyboardInterrupt: # eg. 'Ctrl+Z' or other program interruption
        print('')
        print('Program interrupted by user...')
        break
    except Exception as e: # Some other problems
        print("Unable to retrieve or parse page",url)
        print("Error",e)
        fail = fail + 1
        if fail > 5 : break
        # if there're 5 failures in a row, we're gonna quit
        continue
        # then keep on going

    print(url,len(text))
    # So this far, we've retrieved the URL,
    # and got the number of characters we've retrieved.
    count = count + 1

    # If we got bad data, eg. not start with 'From '
    # All email messages start with "From " (From+space)in the mail list.
    if not text.startswith("From "):
        print(text)
        print("Did not find From ")
        fail = fail + 1
        if fail > 5 : break
        # we'll tolerate up to 5 failures for bad data
        continue

    pos = text.find("\n\n")
    # Find the blank lines
    # "\n\n": a "new line" at the end of a line + another "new line" without strings

    # So we break it into the Mail Headers (a long string before the mail body).
    if pos > 0 :
        hdr = text[:pos]
        body = text[pos+2:]
    else:
        print(text)
        print("Could not find break between headers and body")
        fail = fail + 1
        if fail > 5 : break
        continue

    email = None
    x = re.findall('\nFrom: .* <(\S+@\S+)>\n', hdr)
    # Use a Regular Expression to pull out an email addresses.
    # Email Address format on this web: "From: Name <emailname@organization>"
    if len(x) == 1 : # We should get only one string
        email = x[0];
        email = email.strip().lower()
        email = email.replace("<","")
        # We'll tolerate the little nasty signs in there.
        # So this is kind of clean up.
    else:
        x = re.findall('\nFrom: (\S+@\S+)\n', hdr)
        # if there's no "<>" signs in the email address format
        if len(x) == 1 :
            email = x[0];
            email = email.strip().lower()
            email = email.replace("<","")
            # refine the address, get rid of the bad characters

    # So now we got the good email addresses.
    # Then look for the Email Dates.
    # Email Date format on this web: "Date: Mon, 14 Dec 2005 16:41:01 -0500"
    date = None
    y = re.findall('\Date: .*, (.*)\n', hdr)
    # Pull out all the things after ","
    if len(y) == 1 :
        tdate = y[0]
        tdate = tdate[:26]
        # Chop the whole string off to 26 characters
        try:
            sent_at = parsemaildate(tdate)
            # Parse the date, get back a clean date
        except:
            print(text)
            print("Parse fail",tdate)
            fail = fail + 1
            if fail > 5 : break
            continue

    # Then look for the Email Subjects.
    # Email Subject format on this web: "Subject: Re: Creating a site on collab"
    subject = None
    z = re.findall('\Subject: (.*)\n', hdr)
    if len(z) == 1 : subject = z[0].strip().lower();

    # At this point, we've already parsed and got the information we want.
    # Reset the fail counter,
    # because we kept saying if it fails 5 straight times it quit.
    fail = 0
    print("   ",email,sent_at,subject)
    cur.execute('''INSERT OR IGNORE INTO Messages
        (id, email, sent_at, subject, headers, body)
        VALUES (?,?,?,?,?,?)''',
        (start, email, sent_at, subject, hdr, body) )
    # Insert all the informations into the database.

    if count % 50 == 0 : conn.commit()
    # Every 50 ones we're gonna commit it to speed things up.
    if count % 100 == 0 : time.sleep(1)
    # Every 100 ones we're gonna wait for a second.

conn.commit()
cur.close()
