# This program reads the database, then produces a JavaScript file 'spider.js'.
# Then when we click the already written HTML file 'force.html',
# the HTML file reads 'd3.v2.js' & 'force.js' & 'force.css' and 'spider.js',
# producing the final visualized picture of what we want to see.

# 'd3.v2.js' is the visualization library.

# 'force_js' is just the visualization code,
# which draws the circles, makes the circles' colors, makes them bigger & smaller,
# and connects all the lines in between it.

import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

print("Creating JSON output on spider.js...")
howmany = int(input("How many nodes? "))
# Ask for how many top pages you want to visualize

cur.execute('''SELECT COUNT(from_id) AS inbound, old_rank, new_rank, id, url
    FROM Pages JOIN Links ON Pages.id = Links.to_id
    WHERE html IS NOT NULL AND ERROR IS NULL
    GROUP BY id ORDER BY id,inbound''')
# So we look at the things that have the highest number of Inbound links.

fhand = open('spider.js','w') ## Open or Create a JavaScript file.
nodes = list()
maxrank = None
minrank = None
for row in cur :
    nodes.append(row)
    rank = row[2]
    if maxrank is None or maxrank < rank: maxrank = rank
    if minrank is None or minrank > rank : minrank = rank
    if len(nodes) > howmany : break

if maxrank == minrank or maxrank is None or minrank is None:
    print("Error - please run sprank.py to compute page rank")
    quit()

fhand.write('spiderJson = {"nodes":[\n')
### Start to write out a JavaScript file.
count = 0
map = dict()
ranks = dict()
for row in nodes :
    if count > 0 : fhand.write(',\n')
    # print row
    rank = row[2]
    rank = 19 * ( (rank - minrank) / (maxrank - minrank) )
    # We're basically normalizing the ranks to the thickness of the line,
    # and times the size of the ball '19'(we're visualizing top 20 links )
    fhand.write('{'+'"weight":'+str(row[0])+',"rank":'+str(rank)+',')
    fhand.write(' "id":'+str(row[3])+', "url":"'+row[4]+'"}')
    # Above are just writing some JavaScript with little strings.
    map[row[3]] = count
    ranks[row[3]] = rank
    count = count + 1
fhand.write('],\n') ### Finish the JavaScript.

cur.execute('''SELECT DISTINCT from_id, to_id FROM Links''')
fhand.write('"links":[\n')
# Draw all the lines in the JavaScript.
count = 0
for row in cur :
    # print row
    if row[0] not in map or row[1] not in map : continue
    if count > 0 : fhand.write(',\n')
    rank = ranks[row[0]]
    srank = 19 * ( (rank - minrank) / (maxrank - minrank) )
    # Again normalize things for thickness.
    fhand.write('{"source":'+str(map[row[0]])+',"target":'+str(map[row[1]])+',"value":3}')
    count = count + 1
fhand.write(']};') ### Finish the JavaScript.

fhand.close() ### Close the JavaScript file.

cur.close()
print("Open force.html in a browser to view the visualization")
