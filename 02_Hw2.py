hrs = input("Enter Hours: ")
rate = input("Enter Rate: ")
try:
    h = float(hrs)
    r = float(rate)
except:
    print('Please Enter Numeric Numbers')
    quit()

pay = h * r
print ("Pay: ",pay)
