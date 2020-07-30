import xml.etree.ElementTree as ET
input = '''
<stuff>
    <users>
        <user x="2">
            <id>001</id>
            <name>Chuck</name>
        </user>
        <user x="7">
            <id>009</id>
            <name>Brent</name>
        </user>
    </users>
</stuff>'''

stuff = ET.fromstring(input)
# read 'data' and give us back a 'stuff' object
lst = stuff.findall('users/user')
# find all the child tags in the tag 'users' in a list of tags
print('User count:', len(lst))
# print the number of tags in the list

for item in lst:
    print('Name', item.find('name').text)
    print('Id', item.find('id').text)
    print('Attribute', item.get("x"))
# loop through each tag in the list
