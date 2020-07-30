fname = input('Enter file name: ')
try:
    f = open(fname)
except:
    print('File does not exist.')
    quit()

import re

lst = list()
for line in f :
    digit = re.findall('[0-9]+',line)
    for x in digit:
        num = float(x)
        lst.append(num)
total = int(sum(lst))
print('The sum is',total)
