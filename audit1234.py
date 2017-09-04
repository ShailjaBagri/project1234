
# coding: utf-8

# In[2]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE_sample = "ahmedabad_india.osm"
regex = re.compile(r'\b\S+\.?', re.IGNORECASE)

expected = ["Ahmedabad", "Road", "NR", "Avenue", "SBK", "Gandhi", "Bridge", "Society"] #expected names in the dataset

mapping = {"ahmedabad": "Ahmedabad",
           "Ahmadabad": "Ahmedabad",
           "Ahamadabad": "Ahmedabad",
           "Nr.": "NR",
           "Ave.": "Avenue",
           "sbk": "SBK",
           "gandhi": "Gandhi",
           "bridge": "Bridge",
           "road": "Road",
           "Ft.": "Feet",
           "ft": "Feet",
           "Rd": "Road",
           "Rd.": "Road",
           "rasta": "Road",
           "Roads": "Road",
           "society": "Society",
           "soc.": "Society",
           "Socity": "Society",
           "Gujarat.": "Gujarat,"
            }

# Search string for the regex. If it is matched and not in the expected list then add this as a key to the set.
def audit_street(street_types, street_name): 
    m = regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem): # Check if it is a street name
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile): # return the list that satify the above two functions
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street(street_types, tag.attrib['v'])

    return street_types

pprint.pprint(dict(audit(OSMFILE_sample))) # print the existing names

def string_case(s): # change string into titleCase except for UpperCase
    if s.isupper():
        return s
    else:
        return s.title()

# return the updated names
def update_name(name, mapping):
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
            name[i] = string_case(name[i])
        else:
            name[i] = string_case(name[i])
    
    name = ' '.join(name)
   

    return name

update_street = audit(OSMFILE_sample) 

# print the updated names
for street_type, ways in update_street.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
        print name, "=>", better_name  

'''
In this Section we are going to audit postal codes to check for potential errors. This is a very similar process compared to
to our cleaning street name strategy

'''


zip_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

zip_types = defaultdict(set)

expected_zip = {}

def audit_zip_codes(zip_types, zip_name, regex, expected_zip):
    m = regex.search(zip_name)
    if m:
        zip_type = m.group()
        if zip_type not in expected_zip:
             zip_types[zip_type].add(zip_name)

def is_zip_name(elem):
    return (elem.attrib['k'] == "addr:postcode")


def auditpost(osm_file, regex):
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_zip_name(tag):
                    auditpost_zip_codes(zip_types, tag.attrib['v'], regex, expected_zip)
    pprint.pprint(dict(zip_types))

auditpost(osm_file, zip_type_re)

'''
We want to have all postal codes in the standard 6 digit display. This means we have to change the postal codes that have more
than 6 digits, the ones that beginn with "AZ" and any other ones that differ from the the plain 6 digit display.
'''

for zip_type, ways in zip_types.iteritems(): 
        for name in ways:
            if "-" in name:
                name = name.split("-")[0].strip()
            if "AZ" in name:
                name = name.split("AZ")[1].strip('AZ ')
            print name


# In[ ]:




