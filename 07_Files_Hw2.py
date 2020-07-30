fname = input('Enter file name: ')
try:
    fh = open(fname)
except:
    print('File does not exist.')
    quit()
num = 0
total = 0
for line in fh:
    if not line.startswith('X-DSPAM-Confidence: '):
        continue
    # print(line.rstrip())
    nstart = line.find(':')
    value = float(line[nstart+1:])
    # no need to do : num = strip(num), float will do by itself
    total = total + value
    num = num + 1
print('Average spam confidence:',total/num)
