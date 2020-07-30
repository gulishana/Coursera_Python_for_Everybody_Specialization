# This is a simple code just running a SQL query,
# and then printing stuff out.
import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

cur.execute('''SELECT COUNT(from_id) AS inbound,old_rank,new_rank,id,url
     FROM Pages JOIN Links ON Pages.id = Links.to_id
     WHERE html IS NOT NULL
     GROUP BY id ORDER BY inbound DESC''')

count = 0
for row in cur :
    if count < 50 : print(row)
    count = count + 1
print(count, 'rows.')

# So we just show the number of links,
# and order by the number of Inbound linkes Descending,
# so we see the most linked things and we'll see the top 50 ones of that.

cur.close()
