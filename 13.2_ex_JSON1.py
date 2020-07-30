import json

data = '''
{
  "name" : "Chuck",
  "phone" : {
    "type" : "intl",
    "number" : "+1 734 303 4456"
   },
   "email" : {
     "hide" : "yes"
   }
}'''
# {} turns into a Python dictionary

info = json.loads(data)
# info is a dictionary with (key,value) pairs
print('Name:', info["name"])
print('Hide:', info["email"]["hide"])
# the rest of code are like for Python dictionary
