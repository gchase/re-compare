#!/bin/env python


import  urllib2
import re
from bs4 import BeautifulSoup
import os



def get_pattern_from_file(f_url):
    """
    gets a url for a PROSITE pattern txt file
    return list of patterns

    """

    file_o=urllib2.urlopen(f_url)
    lines=file_o.readlines()
    
    matches=[]

    for l in lines:
        match=re.findall("^PA   (.*)\.$",l)
        if match==[]:
            continue
        else:
            matches.extend(match)
    
    return matches


baseurl="https://prosite.expasy.org/"

page=urllib2.urlopen("https://prosite.expasy.org/cgi-bin/unirule/unirule_browse.cgi?")

html_page=page.read()

soup=BeautifulSoup(html_page)


raw_urls=soup.find_all("a",href=re.compile("PS[0-9]{5}"))

url_suffixes=[re.findall("PS[0-9]{5}",str(r))[0] for r in raw_urls]

actual_urls=[baseurl+r+".txt" for r in url_suffixes]

patterns=[]

for txt in actual_urls:
    patterns.extend(get_pattern_from_file(txt))

write_file=open("protein_patterns","w")

for l in patterns:
    write_file.write(l+"\n")

write_file.close()

