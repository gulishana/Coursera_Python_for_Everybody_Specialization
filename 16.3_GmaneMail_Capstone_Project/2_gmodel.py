# No need to connect to network, thus this only takes a few minutes.
# This is the data cleaning process.
import sqlite3
import time
import re
import zlib
# 'zlib' is a way to do some compressions
from datetime import datetime, timedelta

# Not all systems have this
try:
    import dateutil.parser as parser
except:
    pass

dnsmapping = dict()
mapping = dict()

# Then we create three functions below for cleaning messages from 'content.sqlite'
def fixsender(sender,allsenders=None) :
    global dnsmapping
    global mapping
    if sender is None : return None
    sender = sender.strip().lower()
    sender = sender.replace('<','').replace('>','')

    # Check if we have a hacked gmane.org from address
    if allsenders is not None and sender.endswith('gmane.org') :
        pieces = sender.split('-')
        realsender = None
        for s in allsenders:
            if s.startswith(pieces[0]) :
                realsender = sender
                sender = s
                # print(realsender, sender)
                break
        if realsender is None :
            for s in mapping:
                if s.startswith(pieces[0]) :
                    realsender = sender
                    sender = mapping[s]
                    # print(realsender, sender)
                    break
        if realsender is None : sender = pieces[0]

    mpieces = sender.split("@")
    if len(mpieces) != 2 : return sender
    dns = mpieces[1]
    x = dns
    pieces = dns.split(".")
    if dns.endswith(".edu") or dns.endswith(".com") or dns.endswith(".org") or dns.endswith(".net") :
        dns = ".".join(pieces[-2:])
    else:
        dns = ".".join(pieces[-3:])
    # if dns != x : print(x,dns)
    # if dns != dnsmapping.get(dns,dns) : print(dns,dnsmapping.get(dns,dns))
    dns = dnsmapping.get(dns,dns)
    return mpieces[0] + '@' + dns

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
        # print('Bad Date:',md)
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

# Parse out the info...
def parseheader(hdr, allsenders=None):
    if hdr is None or len(hdr) < 1 : return None
    sender = None
    x = re.findall('\nFrom: .* <(\S+@\S+)>\n', hdr)
    if len(x) >= 1 :
        sender = x[0]
    else:
        x = re.findall('\nFrom: (\S+@\S+)\n', hdr)
        if len(x) >= 1 :
            sender = x[0]

    # normalize the domain name of Email addresses
    sender = fixsender(sender, allsenders)

    date = None
    y = re.findall('\nDate: .*, (.*)\n', hdr)
    sent_at = None
    if len(y) >= 1 :
        tdate = y[0]
        tdate = tdate[:26]
        try:
            sent_at = parsemaildate(tdate)
        except Exception as e:
            # print('Date ignored ',tdate, e)
            return None

    subject = None
    z = re.findall('\nSubject: (.*)\n', hdr)
    if len(z) >= 1 : subject = z[0].strip().lower()

    guid = None
    z = re.findall('\nMessage-ID: (.*)\n', hdr)
    if len(z) >= 1 : guid = z[0].strip().lower()

    if sender is None or sent_at is None or subject is None or guid is None :
        return None
    return (guid, sender, subject, sent_at)


# Here we start to create a new database with clean data.
# This is the normalized database with all kinds of Keys.
conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS Messages ''')
cur.execute('''DROP TABLE IF EXISTS Senders ''')
cur.execute('''DROP TABLE IF EXISTS Subjects ''')
cur.execute('''DROP TABLE IF EXISTS Replies ''')

cur.execute('''CREATE TABLE IF NOT EXISTS Messages
    (id INTEGER PRIMARY KEY, guid TEXT UNIQUE, sent_at INTEGER,
     sender_id INTEGER, subject_id INTEGER,
     headers BLOB, body BLOB)''')
     # 'guid' stands for Global Unique ID
     # 'BLOB': Binary Large Objects, to make compressed fields.
cur.execute('''CREATE TABLE IF NOT EXISTS Senders
    (id INTEGER PRIMARY KEY, sender TEXT UNIQUE)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Subjects
    (id INTEGER PRIMARY KEY, subject TEXT UNIQUE)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Replies
    (from_id INTEGER, to_id INTEGER)''')
    # Table 'Replies' is a connection from one message to another,
    # thus it's like a Many-to-Many database.


# Then we connect to a already constructed database called 'mapping.sqlite'.
# In this DB, we mapped the old email addresses to their new ones.
# So here we just get those information from the DB to correct the messages we've got.
conn_1 = sqlite3.connect('mapping.sqlite')
cur_1 = conn_1.cursor()

cur_1.execute('''SELECT old,new FROM DNSMapping''')
for message_row in cur_1 :
    dnsmapping[message_row[0].strip().lower()] = message_row[1].strip().lower()

mapping = dict()
cur_1.execute('''SELECT old,new FROM Mapping''')
for message_row in cur_1 :
    old = fixsender(message_row[0])
    new = fixsender(message_row[1])
    mapping[old] = fixsender(new)

conn_1.close()
# Done with mapping.sqlite


# Then now we open the main 'content.sqlite' that we want to clean from.
# Here we only open it "Read only",
# so we could potentially be running the spider program '1_gmane.py' together
# with this '2_gmodel.py' cleaning program at the same time.
conn_1 = sqlite3.connect('file:content.sqlite?mode=ro', uri=True)
cur_1 = conn_1.cursor()
# 'conn_1' has closed for 'mapping.sqlite', thus we can use it again for this DB.
# But 'conn' is still open for 'index.sqlite', so we can't use it for now.

allsenders = list()
cur_1.execute('''SELECT email FROM Messages''')
for message_row in cur_1 :
    sender = fixsender(message_row[0])
    if sender is None : continue
    if 'gmane.org' in sender : continue
    if sender in allsenders: continue
    allsenders.append(sender)
    # Take all the email addresses and put those in a list.
print("Loaded allsenders",len(allsenders),"and mapping",len(mapping),"dns mapping",len(dnsmapping))

cur_1.execute('''SELECT headers, body, sent_at
    FROM Messages ORDER BY sent_at''')

senders = dict()
subjects = dict()
guids = dict() # for 'Global Unique IDs'

count = 0

for message_row in cur_1 :
    hdr = message_row[0]
    parsed = parseheader(hdr, allsenders)
    if parsed is None: continue
    (guid, sender, subject, sent_at) = parsed

    # Apply the sender mapping
    sender = mapping.get(sender,sender)

    count = count + 1
    if count % 250 == 1 : print(count,sent_at, sender)
    # Print every 250 things we do.

    if 'gmane.org' in sender:
        print("Error in sender ===", sender)

    sender_id = senders.get(sender,None)
    subject_id = subjects.get(subject,None)
    guid_id = guids.get(guid,None)

    if sender_id is None :
    # means if we haven't seen a 'sender_id' yet
        cur.execute('INSERT OR IGNORE INTO Senders (sender) VALUES (?)', (sender,))
        conn.commit()
        cur.execute('SELECT id FROM Senders WHERE sender=? LIMIT 1', (sender,))
        try:
            row = cur.fetchone()
            sender_id = row[0]
            senders[sender] = sender_id
        except:
            print('Could not retrieve sender id',sender)
            break

    if subject_id is None :
        cur.execute('INSERT OR IGNORE INTO Subjects (subject) VALUES (?)', (subject,))
        conn.commit()
        cur.execute('SELECT id FROM Subjects WHERE subject=? LIMIT 1', (subject,))
        try:
            row = cur.fetchone()
            subject_id = row[0]
            subjects[subject] = subject_id
        except:
            print('Could not retrieve subject id',subject)
            break

    cur.execute('INSERT OR IGNORE INTO Messages (guid,sender_id,subject_id,sent_at,headers,body) VALUES (?,?,?,datetime(?),?,?)',
            ( guid,sender_id,subject_id,sent_at,
            zlib.compress(message_row[0].encode()), zlib.compress(message_row[1].encode()) ) )
    # 'zlib.compress' takes the fields of 'headers' & 'body',
    # and ends up with a compressed version of these stuff,
    # which keeps the size of these things down at the cost of the computation
    # to compress and decompress when we want to read it.
    conn.commit()

    cur.execute('SELECT id FROM Messages WHERE guid=? LIMIT 1', (guid,))
    try:
        row = cur.fetchone()
        message_id = row[0]
        guids[guid] = message_id
    except:
        print('Could not retrieve guid id',guid)
        break

cur.close()  # Close 'index.sqlite' - Clean data
cur_1.close() # Close 'content.sqlite' - Raw data
