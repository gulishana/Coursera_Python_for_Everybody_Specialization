import json

data = '''
[
  { "id" : "001",
    "x" : "2",
    "name" : "Chuck"
  } ,
  { "id" : "009",
    "x" : "7",
    "name" : "Chuck"
  }
]'''
# [] turns into a Python list
info = json.loads(data)
# info is a list of dictionaries
print('User count:', len(info))

for item in info:
    print('Name', item['name'])
    print('Id', item['id'])
    print('Attribute', item['x'])
# the rest of code are like for Python list (of dictionaries)
# JSON dose not have attribute
# you need to know the data structure yourself to get what you need
