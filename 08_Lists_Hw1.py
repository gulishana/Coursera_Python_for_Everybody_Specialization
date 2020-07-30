fname = input('Enter file name: ')
if len(fname)<1:fname='8.1_romeo.txt'
# Press 'Enter' to open 8.1_romeo.txt
try:
    fh = open(fname)
except:
    print('File dose not exist')
    quit()
lst = list()
for line in fh:
    line = line.rstrip()
    wds = line.split()
    for word in wds:
        if word not in lst:
            lst.append(word)
            # not lst=lst.append(word)
lst.sort() # cannot: lst = lst.sort()
print(lst)
