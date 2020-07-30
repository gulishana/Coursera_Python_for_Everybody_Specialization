# This is a Visualization program, which produces 'gword.js'.
# Then the 'gword.htm' program uses 'gword.js' as well as 'd3.js' to create picture.
# 'gword.htm' is just some JavaScript that draws the Word Cloud figure on the page.

import sqlite3
import time
import zlib
import string

conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

cur.execute('SELECT id, subject FROM Subjects')
subjects = dict()
for message_row in cur :
    subjects[message_row[0]] = message_row[1]

cur.execute('SELECT subject_id FROM Messages')
counts = dict()
for message_row in cur :
    text = subjects[message_row[0]]
    text = text.translate(str.maketrans('','',string.punctuation))
    # When the subjects're used more than once,
    # then we count the words more than once.
    # Here 'str.maketrans' throws away all punctuations,
    # so when we make the words, they don't end up with like dashes.
    text = text.translate(str.maketrans('','','1234567890'))
    # Here 'str.maketrans' throws away all numbers.
    text = text.strip() # strip white spaces
    text = text.lower() # convert everything to lowercase
    words = text.split() # split strings by spaces
    for word in words:
        if len(word) < 4 : continue
        counts[word] = counts.get(word,0) + 1

x = sorted(counts, key=counts.get, reverse=True)
highest = None
lowest = None
for k in x[:100]:
    if highest is None or highest < counts[k] :
        highest = counts[k]
    if lowest is None or lowest > counts[k] :
        lowest = counts[k]
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('gword.js','w') # Create a JavaScript file named 'gword.js'.
fhand.write("gword = [") # Start to write out the JavaScript.
first = True
for k in x[:100]:
    if not first : fhand.write( ",\n")
    first = False

    # Below are the text normalization, that tells how big the particular text is.
    size = counts[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * bigsize) + smallsize)

    fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write( "\n];\n") # Finish the JavaScript.

print("Output written to gword.js")
print("Open gword.htm in a browser to see the vizualization")
# So you can double-click 'gword.htm' to see it in the browser.
