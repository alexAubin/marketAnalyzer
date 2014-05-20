#!/usr/bin/env python

import subprocess
import codecs

items = ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen']
systems = ['Jita', 'Rens', 'Amarr']

''' Read items ID '''
itemsID = {}
with codecs.open("info/items.list", 'r', "utf-8-sig") as f:
    for line in f:
       (val, key) = line.split(':')
       itemsID[key.split('\n')[0]] = val

''' Read systems ID '''
systemsID = {}
with codecs.open("info/systems.list", 'r', "utf-8-sig") as f:
    for line in f:
       (val, key) = line.split(':')
       systemsID[key.split('\n')[0]] = val

''' Fetch data '''
for item in items :
    for system in systems :

        url="http://api.eve-central.com/api/quicklook?typeid="+itemsID[item]+"&usesystem="+systemsID[system]+"&setminQ=10000"

        p = subprocess.Popen(["mkdir", "-p", "data/"+item+"/"])
        p.wait()
        p = subprocess.Popen(["wget", "--no-verbose", "-O", "data/"+item+"/"+system+".xml", url])
        p.wait()

