import glob
import py7zr
import os

scriptdir=os.path.abspath(os.path.dirname(__file__))
archives=glob.glob(os.path.join(scriptdir,"**","*.7z"), recursive=True)
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
