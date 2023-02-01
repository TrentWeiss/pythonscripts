#/usr/bin/env python3

import glob
import os
import argparse
from shutil import copyfile, which
import re
import subprocess
import sys
from typing import Union
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
    

parser = argparse.ArgumentParser("Does windeployqt for a library, and also copies over any vcpkg dll dependencies")
parser.add_argument("filepath", type=str, help="What library or directory to deploy qt stuff for.")
parser.add_argument("--extra-paths", nargs="+", default=None, help="Any extra paths to look for dlls on top of the vcpkg bin dir")
parser.add_argument("--vcpkgbin", type=str, default=os.getenv("VCPKG_BIN_DIR"), required=False, help="bin directory of vcpkg installation. Defaults to an environment variable named VCPKG_BIN_DIR")
parser.add_argument("--force", action="store_true", help="Overwrite dlls that already exist in the same directory as \"filepath\"")
parser.add_argument("--depth", type=int, default=3)

args = parser.parse_args()
argdict = vars(args)
print(argdict)
filepath = argdict["filepath"]
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


dependencies_exe : Union[str,None] = which("Dependencies.exe")
if dependencies_exe is None:
    raise FileNotFoundError("Could not find executable \"Dependencies.exe\". is it on your PATH variable?")
dependencies_dir = os.path.dirname(dependencies_exe)
windeployqt_exe : Union[str,None] = which("windeployqt.exe")
if windeployqt_exe is None:
    raise FileNotFoundError("Could not find executable \"windeployqt.exe\". is it on your PATH variable?")
windeployqt_dir = os.path.dirname(windeployqt_exe)
reduced_path = list(str.split(os.getenv("PATH"), sep=os.pathsep))
reduced_path.remove(windeployqt_dir)
reduced_path.remove(dependencies_dir)
reduced_path.remove(os.path.dirname(sys.executable))
wholeenv = dict(os.environ)
reducedenv = {k : str(wholeenv[k]) for k in wholeenv.keys()}
reducedenv["PATH"] = os.pathsep.join(reduced_path)
allreadydeployed = []
while len(filestodeploy)>0:
    filetodeploy : str = filestodeploy.pop(0)
    if filetodeploy in allreadydeployed:
        continue
    print("Deploying stuff for %s" % (filetodeploy,))
    result = subprocess.run([windeployqt_exe, filetodeploy, "--opengl", "--angle"], capture_output=True, text=True)
    print(result.stdout)

    if os.path.basename(filetodeploy) == "python310.dll":
        allmatches = ["zlib1.dll"]
    else:
        expr = re.compile(r"(([a-z]|[A-Z]|[0-9]|[_]|[-]){1}([a-z]|[A-Z]|[0-9]|[_]|[-]|[ ])*(.dll){1})( [\(NOT_FOUND\)|\(ApplicationDirectory\)]){1}")
        result = \
            subprocess.run("%s -chain %s -depth %d" % (dependencies_exe, filetodeploy, argdict["depth"]),\
                capture_output=True, text=True, env=reducedenv)
        # print(result.stdout)
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

        