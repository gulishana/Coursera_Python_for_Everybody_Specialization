def computepay(h,r):
    if h>40:
        p = 40*r+(h-40)*1.5*r
    else:
        p = h * r
    return p

hrs = input("Enter Hours: ")
rate = input("Enter Rate: ")
try:
    h=float(hrs)
    r=float(rate)
except:
    print('Please Enter Number')
    quit()
p = computepay(h,r)
print('Pay:',p)
