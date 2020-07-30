fname = input('Enter file name: ')
if len(fname)<1:fname='7.1_words.txt'
# Press 'Enter' to open 7.1_words.txt
try:
    fh = open(fname)
except:
    print('File does not exist.')
    quit()
content = fh.read() # read the file content
content = content.upper()
content = content.rstrip() #strip the \n at the end of the text
print(content)

# OR

fname= input('Enter file name: ')
fh = open(fname)
print(fh)   #Only print the handle typy
for lx in fh:  # read each line and print out in upper case
    ly = lx.rstrip() #stip the \n at the end of each line
    print(ly.upper())
