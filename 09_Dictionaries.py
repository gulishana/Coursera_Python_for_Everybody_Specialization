name = input('Enter file name: ')
if len(fname)<1:fname='7.2_mbox-short.txt'
# Press 'Enter' to open 7.2_mbox-short.txt
try:
    file = open(name)
except:
    print('File does not exist')
    quit()

emails = dict()
for line in file:
    line = line.rstrip()
    wds = line.split()
    if len(wds)<2 or wds[0]!='From':
        continue
    word = wds[1]
    emails[word] = emails.get(word,0) + 1
    # if word is not in emails, the key 'word' gets default value=0

ads = None
num = None
for key, value in emails.items(): # Tuples
    if num is None or value>num: # compound statement
        ads = key
        num = value
print(ads,num)
