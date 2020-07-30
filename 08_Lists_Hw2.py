fname = input('Enter file name: ')
if len(fname)<1:fname='7.2_mbox-short.txt'
# Press 'Enter' to open 7.2_mbox-short.txt
try:
    fh = open(fname)
except:
    print('File dose not exist')
    quit()
count = 0
for line in fh:
    if line.startswith('From '):
        #'From ' blank is necessary,otherwise will count twice
        wds = line.split()
        print(wds[1])
        count = count + 1
print('There were',count,'lines in the file with From as the first word')


# OR
for line in fname:
    line = line.rstrip()
    wds = line.split()
    # Skip Blank Lines & guardian in a compound statement
    if len(wds) <3 or wds[0] != 'From':
        continue
    print(wds[1])
