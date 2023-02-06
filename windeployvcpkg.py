#/usr/bin/env python3

import glob
import os
import argparse
from shutil import copyfile, which
import re
import subprocess
import sys
from typing import Union
import dlldiag, dlldiag.common
class DLLPath:
    def __init__(self, dll, folder) -> None:
        self.dll = dll
        self.folder = folder
    def __eq__(self, __o : Union[str, 'DLLPath']) -> bool:
        t = type(__o)
        if t == DLLPath:
            return self.dll == __o.dll
        elif t == str:
            return self.dll==__o
        else:
            return False
    

parser = argparse.ArgumentParser("Recursively copy any vcpkg dll dependencies for a specified binary. Optionally call windeployqt as well.")
parser.add_argument("filepath", type=str, help="What library or directory to deploy qt stuff for.")
parser.add_argument("--extra-paths", nargs="+", default=None, help="Any extra paths to look for dlls on top of the vcpkg bin dir")
parser.add_argument("--vcpkgbin", type=str, default=os.getenv("VCPKG_BIN_DIR"), required=False, help="bin directory of vcpkg installation. Defaults to an environment variable named VCPKG_BIN_DIR")
parser.add_argument("--force", action="store_true", help="Overwrite dlls that already exist in the same directory as \"filepath\"")
parser.add_argument("--exe-dlls", action="store_true", help="Also copy over dll files found in the \"DLLs\" subfolder of the directory containing python.exe")
parser.add_argument("--depth", type=int, default=3)
parser.add_argument("--qt", action="store_true", help="Also call windeployqt.exe on the specified module.")

args = parser.parse_args()
argdict = vars(args)
print(argdict)
filepath = argdict["filepath"]
useqt = argdict["qt"]
filestodeploy = []
if os.path.isfile(filepath):
    filedir = os.path.dirname(filepath)
    filestodeploy.append(filepath)
elif os.path.isdir(filepath):
    filedir = filepath
    for entry in os.scandir(path=filedir) :
        if entry.is_file() and entry.name.endswith(".pyd"):
            filestodeploy.append(os.path.join(filedir, entry.name))
else:
    raise ValueError("%s is not a file or directory" % (filepath,))
vcpkgbin = argdict["vcpkgbin"]
if vcpkgbin is None:
    raise ValueError("you must either specify a vcpkg binary directory with --vcpkgbin or set the VCPKG_BIN_DIR environment variable")
vcpkgroot = os.path.abspath(os.path.join(vcpkgbin,".."))
vcpkgbinaries : set = {os.path.basename(f) for f in set(glob.glob(os.path.join(vcpkgbin,"*.dll"),recursive=False))}
extrabinaries : set = set()
extrabinaries
force = argdict["force"]
if argdict["extra_paths"] is not None:
    extra_paths = list(argdict["extra_paths"])
    for path in extra_paths:
        extrabinaries = extrabinaries.union({f for f in set(glob.glob(os.path.join(path,"*.dll"), recursive=False)) if os.path.basename(f) not in vcpkgbinaries})


reduced_path = list(str.split(os.getenv("PATH"), sep=os.pathsep))
dlldiag_exe : Union[str,None] = which("dlldiag.exe")
if dlldiag_exe is None:
    raise FileNotFoundError("Could not find executable \"dlldiag.exe\". is the pip package dll-diagnostics installed?")
dlldiag_dir = os.path.dirname(dlldiag_exe)
reduced_path.remove(dlldiag_dir)
if useqt:
    windeployqt_exe : Union[str,None] = which("windeployqt.exe")
    if windeployqt_exe is None:
        raise FileNotFoundError("Could not find executable \"windeployqt.exe\". is it on your PATH variable?")
    windeployqt_dir = os.path.dirname(windeployqt_exe)
    reduced_path.remove(windeployqt_dir)
exedir = os.path.dirname(sys.executable)
reduced_path.remove(exedir)
for path in reduced_path:
    if not os.path.exists(path):
        reduced_path.remove(path)
        continue
    if (not path==exedir) and (not path==dlldiag_dir) and (vcpkgroot in path):
        reduced_path.remove(path)
    for entry in os.scandir(path):
        if entry.is_file() and (entry.name in vcpkgbinaries) and (entry.name in reduced_path):
            reduced_path.remove(path)
wholeenv = dict(os.environ)
reducedenv = {k : str(wholeenv[k]) for k in wholeenv.keys()}
reducedenv["PATH"] = os.pathsep.join(reduced_path)
print(reducedenv["PATH"])
allreadydeployed = []

expr = re.compile(r"(([a-z]|[A-Z]|[0-9]|[_]|[-]|[.])+(.dll)){1}([ ]|[\t])+Error")
if argdict["exe_dlls"]:
    systemdlls = set(glob.glob(os.path.join(exedir, "DLLs", "*.dll"),recursive=False))
    for dll in systemdlls:
        print("Copying exe folder dll %s to %s" % (dll, filedir))
        destfile = os.path.join(filedir, os.path.basename(dll))
        copyfile(dll, destfile)
while len(filestodeploy)>0:
    filetodeploy : str = filestodeploy.pop(0)
    if filetodeploy in allreadydeployed:
        continue
    print("Deploying stuff for %s" % (filetodeploy,))
    if useqt:
        result = subprocess.run([windeployqt_exe, filetodeploy, "--opengl", "--angle"], capture_output=True, text=True)
        print(result.stdout)
    result = \
        subprocess.run("%s deps %s --show all" % (dlldiag_exe, filetodeploy),\
            capture_output=True, text=True, env=reducedenv)
    allmatches = [ elem[0] for elem in re.findall(expr, result.stdout)]
    for match in allmatches:
        if match in vcpkgbinaries:
            fullmatch = os.path.join(vcpkgbin, match)
            destfile = os.path.join(filedir, match)
            if force or (not os.path.exists(destfile)):
                print("Copying vcpkg binary %s to %s" % (fullmatch, filedir))
                copyfile(fullmatch, destfile)
            filestodeploy.append(destfile)
        else:
            for extrabinary in extrabinaries:
                extrabinary_base = os.path.basename(extrabinary)
                if match == extrabinary_base:
                    destfile = os.path.join(filedir, match)
                    if force or (not os.path.exists(destfile)):
                        print("Copying extra binary %s to %s" % (extrabinary, filedir))
                        copyfile(extrabinary, destfile)
                    filestodeploy.append(destfile)
                    break

    allreadydeployed.append(filetodeploy)

        