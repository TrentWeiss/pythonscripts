#/usr/bin/env python3

import glob, os, argparse, json
parser = argparse.ArgumentParser("Unpack the vcpkg manifest into a list of packages to install")
parser.add_argument("manifest", type=str, help=".json file containing the vcpkg manifest")
parser.add_argument("--packages-skip", nargs='+', default="", help="Packages to skip")
parser.add_argument("--triplets-skip", nargs='+', default="", help="Triplets to skip")
args = parser.parse_args()
argdict = vars(args)
with open(argdict["manifest"], "r") as f:
    vcpkgdict = json.loads(f.read().strip("'<>() "))
packages_skip = list(argdict["packages_skip"])
triplets_skip = list(argdict["triplets_skip"])
package_commands = []
for package in vcpkgdict.values():
    name = package["package_name"]
    if name in packages_skip:
        continue
    triplet = package["triplet"]
    if triplet in triplets_skip:
        continue
    features = package["features"]
    if len(features)>0:
        name+= "[%s]" % (",".join(features),)
    command = "%s:%s" % (name,triplet)
    package_commands.append(command)

    #print(package)
#print(package_commands)
print("./vcpkg install %s" % (" ".join(package_commands)) )

