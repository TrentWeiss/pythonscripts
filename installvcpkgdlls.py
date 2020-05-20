#/usr/bin/env python

import glob, os, argparse
from shutil import copyfile
parser = argparse.ArgumentParser("Automatically copy dll dependencies from vcpkg. Recursively searches a build tree for dll files that vcpkg copied in as part of the build.  This script then copies that file to a specified install directory IF AND ONLY IF that same dll file is also found in a specified vcpkg bin folder.")
parser.add_argument("buildpath", type=str, help="Recursively search this folder for .dll files")
parser.add_argument("installbin", type=str, help="Where to put the found dlls if they are part of a vcpkg installation")
parser.add_argument("--vcpkgbin", type=str, default=os.getenv("VCPKG_BIN_DIR"), required=False, help="bin directory of vcpkg installation. Defaults to an environment variable named VCPKG_BIN_DIR")
parser.add_argument("--force", action="store_true", help="Overwrite dlls that already exist in the installbin folder")
args = parser.parse_args()
buildpath = args.buildpath
installbin = args.installbin
vcpkgbin = args.vcpkgbin
force=args.force
if vcpkgbin is None:
    raise ValueError("you must either specify a vcpkg binary directory with --vcpkgbin or set the VCPKG_BIN_DIR environment variable")
files = glob.glob(os.path.join(buildpath,"**","*.dll"),recursive=True)
files = list(set([os.path.basename(f) for f in files]))
for basefile in files:
    installfile = os.path.join(installbin,basefile)
    vcpkgfile = os.path.join(vcpkgbin,basefile)
    if os.path.exists(vcpkgfile) and ((not os.path.exists(installfile)) or force) :
        print("Installing " + vcpkgfile + " to " + installfile)
        copyfile(vcpkgfile, installfile)
        
    #print(basefile)
