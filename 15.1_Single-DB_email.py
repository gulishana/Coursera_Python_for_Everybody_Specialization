import sqlite3

con = sqlite3.connect('emaildb.sqlite')
cur = con.cursor()

cur.execute('''DROP TABLE IF EXISTS Counts''')
cur.execute('''CREATE TABLE Counts (org TEXT, count INTEGER)''')

fname = input('Enter file name: ')
if (len(fname)<1) : fname='15_mbox.txt'
try:
    fh = open(fname)
except:
    print('File does not exist.')
    quit()

for line in fh:
    if not line.startswith('From: '): continue
    email = line.split()[1]
    org = email.split('@')[1]
    cur.execute('SELECT count FROM Counts WHERE org=?',
    (org,) )
    row = cur.fetchone()
    if row is None:
        cur.execute('''
        INSERT INTO Counts (org,count) VALUES (?,1)''',
        (org,) )
    else:
        cur.execute('UPDATE Counts SET count=count+1 WHERE org=?',
        (org,) )
    con.commit()

sqlstr = 'SELECT org,count FROM Counts ORDER BY count DESC'
# here cannot use (org,count) with ()
for rows in cur.execute(sqlstr):
    print(str(rows[0]), rows[1])
cur.close()
