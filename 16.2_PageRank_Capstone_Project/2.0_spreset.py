# This program allows us to restart the Page Rank Algorithm if we want.
# But here we don't need it and we're not gonna play with this.
import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

cur.execute('''UPDATE Pages SET new_rank=1.0, old_rank=0.0''')
conn.commit()

cur.close()

print("All pages set to a rank of 1.0")
