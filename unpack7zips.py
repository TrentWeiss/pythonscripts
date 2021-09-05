import glob
import py7zr
import os
import argparse

parser = argparse.ArgumentParser(description="Unpack all .7z files in a specified directory")
parser.add_argument("root_dir", help="Where to search for .7z files")
args = parser.parse_args()



root_dir=os.path.abspath(args.root_dir)
archives=glob.glob(os.path.join(root_dir,"**","*.7z"), recursive=True)
print(archives)
for archivepath in archives:
  archivedir = os.path.dirname(archivepath)
  archivefile = os.path.basename(archivepath)
  archivecontent = os.path.splitext(archivefile)[0]
  print(archivecontent)
  if os.path.isdir(os.path.join(archivedir, archivecontent)):
    continue
  print("Extracting 7z file: %s" % (archivepath))
  archive = py7zr.SevenZipFile(archivepath, mode='r')
  archive.extractall(path=archivedir)
  archive.close()
