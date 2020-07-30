import xml.etree.ElementTree as ET
# 'ElementTree' is the built-in XML parser in Python
# 'ET' gives us a shortcut handle for 'ElementTree'

data = '''
<person>
  <name>Chuck</name>
  <phone type="intl">
     +1 734 303 4456
   </phone>
   <email hide="yes"/>
</person>'''
# This is emulating structured XML information
# not from a real web page, thus only works as a string

tree = ET.fromstring(data)
# read 'data' and give us back a 'tree' object
# if there's mistake in the XML structure, this may fail
print('Name:', tree.find('name').text)
# fine tag 'name', and grab the text of the tag
print('Attr:', tree.find('email').get('hide'))
# fine tag 'email', and grab the content of the attribute 'hide'
