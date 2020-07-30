import socket

mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# make a socket, not connected yet
mysock.connect( ('data.pr4e.org', 80) )
# make connet to the internet with a (domain name,port number)
cmd = 'GET http://data.pr4e.org/intro-short.txt HTTP/1.0\r\n\r\n'.encode()
# send HTTP command, \n\n are blank lines
# .encode() converts from 'Unicode' internally to 'UTF-8' to be sent out
mysock.send(cmd)
# send the UTF-8 bytes out, and wait for response

while True:
    data = mysock.recv(512)
    # ask to recieve up to 512 characters and get that back
    if (len(data) < 1):
        break
        # if get no data back, means the end of data, then quit
    print(data.decode())
    # print the data and reversely use .decode() to convert UTF-8 back to Unicode
mysock.close()
# close the connection when it's all done
