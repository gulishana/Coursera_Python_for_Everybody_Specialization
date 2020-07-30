name = input('Enter file name: ')
if len(fname)<1:fname='7.2_mbox-short.txt'
# Press 'Enter' to open 7.2_mbox-short.txt
try:
    file = open(name)
except:
    print('File does not exist')
    quit()

dis = dict()
for line in file:
    line = line.rstrip()
    wds = line.split()
    if len(wds)<2 or wds[0]!='From':
        continue
    word = wds[5]
    time = word.split(':')
    time = time[0]
    dis[time] = dis.get(time,0) + 1

counts = sorted(dis.items()) # Show from Samll to Big, thus NO reverse
for key,value in counts:
    print(key,value)
