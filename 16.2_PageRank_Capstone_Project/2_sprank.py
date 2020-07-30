import sqlite3
# Now we've already got the database, thus we don't need to connect the network
# It's only updating two columns of Page Table: (old_rank, new_rank)

conn = sqlite3.connect('spider.sqlite') 
# 'spider_chuck100.sqlite'
# 'spider_?.sqlite'
cur = conn.cursor()

# Find the IDs that send out page rank - we only are interested
# in pages in the SCC that have in and out links
cur.execute('''SELECT DISTINCT from_id FROM Links''')
# 'SELECT DISTINCT' throws out any duplicates
from_ids = list()
for row in cur:
    from_ids.append(row[0])
# So by 'from_id's we got all the pages that have links to other pages.

# And we're also gonna go to look at the pages that receive page ranks.
to_ids = list()
links = list()
cur.execute('''SELECT DISTINCT from_id, to_id FROM Links''')
for row in cur:
    from_id = row[0]
    to_id = row[1]
    # We're not interested in the following 3 links:
    if from_id == to_id : continue
    if from_id not in from_ids : continue
    if to_id not in from_ids : continue
    # This means the to_id is pointing off to nowhere,
    # or point to pages that we haven't retrieved yet.
    # Thus these are only the links that point to another page we've already retrieved.
    links.append(row)
    if to_id not in to_ids : to_ids.append(to_id)
# So this is getting what's called the Stongly Connected Component,
# which means any of these IDs, there's a path from every ID to every other ID.
# So that's called the Stongly Connected Component in Graph Theory.

# Get latest page ranks for strongly connected component.
prev_ranks = dict()
for node in from_ids:
    cur.execute('''SELECT new_rank FROM Pages WHERE id = ?''', (node, ))
    row = cur.fetchone()
    prev_ranks[node] = row[0]


sval = input('How many iterations:')
many = 1
if ( len(sval) > 0 ) : many = int(sval)

# Sanity check
if len(prev_ranks) < 1 : # Check to see if there's any value in there.
    print("Nothing to page rank.  Check data.")
    quit()

# Lets do Page Rank in memory so it is really fast
for i in range(many):
    # print prev_ranks.items()[:5]
    next_ranks = dict();
    total = 0.0
    for (node, old_rank) in list(prev_ranks.items()):
    # It's gonna take the previous page rank,
    # which is the mapping of PrimaryKey to old page rank,
    # and loop through them.
        total = total + old_rank
        next_ranks[node] = 0.0
    # print total

    # Find the number of Outbound links for each page rank item,
    # and sent the page rank down each
    for (node, old_rank) in list(prev_ranks.items()):
        # print node, old_rank
        give_ids = list() # these're the IDs we're gonna give it to
        for (from_id, to_id) in links:
            if from_id != node : continue
            # for a particular 'node', we're gonna go through the Outbound links,
            # and choose the one that does not link to itself.
            if to_id not in to_ids: continue
            give_ids.append(to_id)
            # 'give_ids' are the IDs that 'node' is gonna share its goodness
        if ( len(give_ids) < 1 ) : continue
        amount = old_rank / len(give_ids)
        # Calculate how much goodness we're gonna flow Outbound,
        # based on the previous rank of the particular 'node' - 'old_rank',
        # and the number of Outbound links - 'len(give_ids)'.

        for id in give_ids:
            next_ranks[id] = next_ranks[id] + amount
        # For all the IDs we're giving it to,
        # we started with the 'next_ranks' being 0 for these folks.
        # These're the receiving end,
        # and we're gonna add the 'amount' of page rank to each one.

    newtot = 0 # newtotal
    for (node, next_rank) in list(next_ranks.items()):
        newtot = newtot + next_rank
    evap = (total - newtot) / len(next_ranks)  # Evaporative Factor!!!
    # There're dysfunctional shapes in which PageRank can be trapped.
    # This 'evaporation  is taking a fraction away from everyone,
    # and giving it back to everybody else.

    for node in next_ranks:
        next_ranks[node] = next_ranks[node] + evap

    newtot = 0
    for (node, next_rank) in list(next_ranks.items()):
        newtot = newtot + next_rank

    # Calculate the average difference between the page ranks.
    # Compute the per-page average change from old rank to new rank.
    # As indication of Convergence of the Algorithm.
    # This is telling us the Stability of the page rank.
    # From one iteration to the next,the more it changes,the least stable it is.
    totdiff = 0
    for (node, old_rank) in list(prev_ranks.items()):
        new_rank = next_ranks[node]
        diff = abs(old_rank-new_rank)
        totdiff = totdiff + diff

    avediff = totdiff / len(prev_ranks)
    # Calculate the average difference in the page ranks per node?
    print(i+1, avediff)

    # Rotate: take the new ranks and make them the old ranks,
    # and then run loop again.
    prev_ranks = next_ranks


# Put the final ranks back into the database
print(list(next_ranks.items())[:5])
cur.execute('''UPDATE Pages SET old_rank=new_rank''')
for (id, new_rank) in list(next_ranks.items()) :
    cur.execute('''UPDATE Pages SET new_rank=? WHERE id=?''', (new_rank, id))

conn.commit()
cur.close()
