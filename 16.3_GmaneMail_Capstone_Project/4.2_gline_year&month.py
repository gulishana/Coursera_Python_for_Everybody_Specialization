# This is another Visualization program, which produces 'gline.js'.
# Then the 'gline.htm' program uses 'gline.js' as well as 'd3.js' to create picture.
# 'gline.htm' is just some JavaScript that draws the Line Chart on the page.

import sqlite3
import time
import zlib

conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

# Pre-load all of the 'sender's in this case.
cur.execute('SELECT id, sender FROM Senders')
senders = dict() # create a dictionary of "senders"
for message_row in cur :
    senders[message_row[0]] = message_row[1]

# Pre-load all the messages.
cur.execute('SELECT id,guid,sender_id,subject_id,sent_at FROM Messages')
messages = dict() # create a dictionary of "all messages"
for message_row in cur :
    messages[message_row[0]] = (message_row[1],message_row[2],message_row[3],message_row[4])

print("Loaded messages=",len(messages),"senders=",len(senders))

sendorgs = dict() # create a dictionary of "sending organizaitons"
for (message_id, message) in list(messages.items()):
    sender = message[1]
    pieces = senders[sender].split("@")
    if len(pieces) != 2 : continue
    dns = pieces[1]
    sendorgs[dns] = sendorgs.get(dns,0) + 1

# Pick the Top Schools as Top Sending Organizaitons.
orgs = sorted(sendorgs, key=sendorgs.get, reverse=True)
orgs = orgs[:10] # 'orgs' are only Top 10 Organizations.
print("Top 10 Organizations: ")
print(orgs)

# Here we're gonna show the message count by Month.
counts = dict()
months = list()

for (message_id, message) in list(messages.items()):
    sender = message[1]
    pieces = senders[sender].split("@")
    if len(pieces) != 2 : continue
    dns = pieces[1]
    if dns not in orgs : continue # Find dns only in the Top 10 Organizaions.
    month = message[3][:7] 
    # From 0th to 6th, not including 7th.
    # Month is the first 7 characters of date (field 'sent_at'), eg. "2005-12".
    if month not in months : months.append(month)
    key = (month, dns)
    # 'key' is a tuple, inlcuding Month and 'dns' (which organizaiton did it).
    # And it's only in the Top 10 Organizaions.
    counts[key] = counts.get(key,0) + 1
    # So we just create a dictionary where the Key is a tuple.

months.sort()
# Sort by Key, which is the Month in this case, not by Value.
# print counts
# print months


fhand = open('gline.js','w') # Create a JavaScript file named 'gline.js'.
fhand.write("gline = [ ['Year'") # Start to write out the JavaScript.
for org in orgs:
    fhand.write(",'"+org+"'")
fhand.write("]")

for month in months:
    fhand.write(",\n['"+month+"'")
    for org in orgs:
        key = (month, org)
        val = counts.get(key,0)
        fhand.write(","+str(val))
    fhand.write("]");

fhand.write("\n];\n") # Finish the JavaScript.

print("Output written to gline.js")
print("Open gline.htm to visualize the data")
# So you can double-click 'gline.htm' to see it in the browser.
