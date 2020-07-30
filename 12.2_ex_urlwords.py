import urllib.request, urllib.parse, urllib.error

fhand = urllib.request.urlopen('http://data.pr4e.org/romeo.txt')
# open the URL just like opening a file into a file handle
counts = dict()
for line in fhand:
    words = line.decode().split()
    for word in words:
        counts[word] = counts.get(word, 0) + 1
print(counts)
# all these are the same as treating a file
# only difference is to Decode Byte into String first
# then the rest are all the same as opening a file
