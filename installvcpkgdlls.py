import glob, os, argparse
from shutil import copyfile
parser = argparse.ArgumentParser("Automatically copy dll dependencies from vcpkg")
parser.add_argument("buildpath", type=str)
parser.add_argument("installbin", type=str)
parser.add_argument("vcpkgbin", type=str)
args = parser.parse_args()
buildpath = args.buildpath
installbin = args.installbin
vcpkgbin = args.vcpkgbin
files = glob.glob(os.path.join(buildpath,"**","*.dll"),recursive=True)
for f in files:
    basefile = os.path.basename(f)
    installfile = os.path.join(installbin,basefile)
    vcpkgfile = os.path.join(vcpkgbin,basefile)
    if (not os.path.exists(installfile)) and os.path.exists(vcpkgfile):
        print("Installing " + vcpkgfile + " to " + installfile)
        copyfile(vcpkgfile, installfile)
        
    #print(basefile)
