#/usr/bin/env python3

import glob, os, argparse, json, re
parser = argparse.ArgumentParser("Fixes type definitions in a file to match the ROS2 IDL")
parser.add_argument("inputfile", type=str, help="The file to fix up")
args = parser.parse_args()
argdict = dict(vars(args))
with open(argdict["inputfile"], "r") as f:
    lines = f.readlines()
for line in lines:
    
    nospaces = line.replace(" ","")
    if nospaces=="" or nospaces[0]=="#":
        continue
    (typename, varname) = str.split(line.replace("\n",""))
    typename = typename.replace("octet","byte")
    typename = typename.replace("double","float64")
    fixup = re.sub('([A-Z]{1})', r'_\1', varname).lower().replace(" _"," ")
    fixup2 = re.sub('([A-Z]{1})', r'_\1', fixup).lower().replace(" _"," ")
    arraymatch = (re.search('(\[[0-9]\]{1})', fixup2))
    if arraymatch is not None:
        g = arraymatch.group(0)
       # print(g)
        typename = typename + g
        fixup2 = fixup2.replace(g,"")
    print(typename + " " + fixup2)