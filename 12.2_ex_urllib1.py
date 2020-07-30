import urllib.request, urllib.parse,urllib.error

fhand = urllib.request.urlopen('http://data.pr4e.org/romeo.txt')
# make a connection to the web page without open the Headers
for line in fhand:
    print(line.decode().strip())
    # decode the Byte into String and do stuff with them
