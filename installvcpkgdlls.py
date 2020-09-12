#/usr/bin/env python3

import glob, os, argparse
from shutil import copyfile
parser = argparse.ArgumentParser("Automatically copy dll dependencies from vcpkg. Recursively searches a build tree for dll files that vcpkg copied in as part of the build.  This script then copies that file to a specified install directory IF AND ONLY IF that same dll file is also found in a specified vcpkg bin folder.")
parser.add_argument("--buildpath", type=str, help="Recursively search this folder for .dll files. Defaults to .\\build", default=".\\build")
parser.add_argument("--installbin", type=str, help="Where to put the found dlls if they are part of a vcpkg installation.  Defaults to .\\install\\bin", default=".\\install\\bin")
parser.add_argument("--vcpkgbin", type=str, default=os.getenv("VCPKG_BIN_DIR"), required=False, help="bin directory of vcpkg installation. Defaults to an environment variable named VCPKG_BIN_DIR")
parser.add_argument("--force", action="store_true", help="Overwrite dlls that already exist in the installbin folder")
parser.add_argument("--extra-libs", nargs="+", default=None, help="Copy dlls matching these glob-style patterns in the vcpkg binary folder, even if they are not found in the build path")
args = parser.parse_args()
argdict = vars(args)
print(argdict)
buildpath = argdict["buildpath"]
installbin = argdict["installbin"]

vcpkgbin = argdict["vcpkgbin"]
if vcpkgbin is None:
    raise ValueError("you must either specify a vcpkg binary directory with --vcpkgbin or set the VCPKG_BIN_DIR environment variable")

force = argdict["force"]

if argdict["extra_libs"] is not None:
    extra_libs = list(argdict["extra_libs"])
else:
    extra_libs = []
    
vcpkgbinaries = {os.path.basename(f) for f in set(glob.glob(os.path.join(vcpkgbin,"*.dll"),recursive=False))}
filesinbuild = {os.path.basename(f) for f in set(glob.glob(os.path.join(buildpath,"**","*.dll"),recursive=True))}
filestoinstall = filesinbuild.intersection(vcpkgbinaries)

extra_lib_set = set()
for pattern in extra_libs:
    extravcpkgfiles = [os.path.basename(f) for f in glob.glob(os.path.join(vcpkgbin,pattern),recursive=False)]
    extra_lib_set.update(set(extravcpkgfiles))
filestoinstall.update(extra_lib_set)

for basefile in filestoinstall:
    installfile = os.path.join(installbin,basefile)
    vcpkgfile = os.path.join(vcpkgbin,basefile)
    if os.path.exists(vcpkgfile) and ((not os.path.exists(installfile)) or force) :
        print("Installing " + vcpkgfile + " to " + installfile)
        copyfile(vcpkgfile, installfile)

        