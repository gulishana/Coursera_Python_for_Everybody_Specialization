largest = None
smallest = None
while True:   #infinite loop: run the loop until break out
    num = input('Enter a number: ')
    if num == 'done':
        break
    try:
        n = int(num) #require integer, not float point variable
    except:
        print('Invalid input')
        continue
    #print(n)
    if smallest is None: #First, argue for 'smallest'
        smallest = n
    elif n < smallest:
        smallest = n
    if largest is None: #Then, argue for 'largest'
        largest = n
    elif n > largest:
        largest = n
print('Maximum is',largest)
print('Minimum is',smallest)
