import argparse
import glob
import os
import xml
from shutil import copyfile
import shutil
parser = argparse.ArgumentParser("Patch all xml files in a directory to refer to bin/<filename> instead of lib/lib<filename>.")
parser.add_argument("--srcdir", type=str, help="Recursively search this folder for .xml files", default=".\\src")
args = parser.parse_args()
argdict = vars(args)
srcdir = argdict["srcdir"]



search_string = "<library path=\"lib/lib"
replace_string = "<library path=\"bin/"

files = list(glob.glob(os.path.join(srcdir,"**","*.xml"),recursive=True))
files = [f for f in files if not os.path.basename(f)=="package.xml"]
for fpath in files:
    print("Opening %s" %(fpath))
    with open(fpath,"r") as f:
        strin = str(f.read())
        strout = strin.replace(search_string, replace_string)
        #idxfind = strin.find(search_string)
        # if idxfind>=0:
        #     print("Found a match in file %s. Matching text: %s" % (fpath, strin[idxfind:idxfind+len(search_string)]) )
    if not strout==strin:
        with open(fpath,"w") as f:
            f.write(strout)
