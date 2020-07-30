text = 'X-DSPAM-Confidence:    0.8475';
nstart = text.find('0')
nend = text.find('5')
num = float(text[nstart:nend+1])
print(num)


#OR
text = 'X-DSPAM-Confidence:    0.8475';
nstart = text.find(':')
num = text[nstart+1:]
# no need to do : num = strip(num), float will do by itself
num = float(num)
print(num)
