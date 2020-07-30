import json
import sqlite3

con = sqlite3.connect('15.3_rosterdb.sqlite')
cur = con.cursor()

cur.executescript('''
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Member;
CREATE TABLE User(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE);
CREATE TABLE Course(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title TEXT UNIQUE);
CREATE TABLE Member(
    user_id INTEGER, course_id INTEGER, role INTEGER,
    PRIMARY KEY (user_id,course_id) );
''')

fname = input('Enter file name:')
if len(fname)<1 : fname = '15.3_roster_data.json'

data = open(fname).read()
js = json.loads(data)
print('(Person,Course) Count',len(js))

for item in js :
    name = item[0]
    title = item[1]
    role = item[2]
    #print((name,title))

    cur.execute('''INSERT OR IGNORE INTO User (name)
        VALUES (?)''',(name,))
    cur.execute('SELECT id FROM User WHERE name=?',(name,))
    user_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Course (title)
        VALUES (?)''',(title,))
    cur.execute('SELECT id FROM Course WHERE title=?',(title,))
    course_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Member
        (user_id,course_id,role) VALUES (?,?,?)''',
        (user_id,course_id,role))

    con.commit()

cur.close()
