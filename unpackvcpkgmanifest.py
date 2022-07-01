#/usr/bin/env python3

import glob, os, argparse, json
class keyvalue(argparse.Action): 
    # Constructor calling 
    def __call__( self , parser, namespace, 
                 values, option_string = None): 
        setattr(namespace, self.dest, dict()) 
          
        for value in values: 
            # split it into key and value 
            key, value = value.split('=') 
            # assign into dictionary 
            getattr(namespace, self.dest)[key] = value



parser = argparse.ArgumentParser("Unpack the vcpkg manifest into a list of packages to install")
parser.add_argument("manifest", type=str, help=".json file containing the vcpkg manifest")
parser.add_argument("--packages-skip", nargs='+', default="", help="Packages to skip")
parser.add_argument("--triplets-skip", nargs='+', default="", help="Triplets to skip")
parser.add_argument("--replace-triplets", nargs='*', action=keyvalue, help="arbitrary number of triplet replacements of the form <triplet1>=<triplet2>. All packages installed on <triplet1> will instead be output as <triplet2>")
args = parser.parse_args()
argdict = vars(args)
with open(argdict["manifest"], "rb") as f:
    blob : bytes = f.read()
try:
    vcpkgdict = json.loads(blob.decode("utf-8-sig").strip("'<>() "))
except:
    vcpkgdict = json.loads(blob.decode("utf-16").strip("'<>() "))

packages_skip = list(argdict["packages_skip"])
triplets_skip = list(argdict["triplets_skip"])
triplet_replacements = argdict["replace_triplets"]
if triplet_replacements is None:
    triplet_replacements = {}
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
    triplet = triplet_replacements.get(triplet,triplet)
    command = "%s:%s" % (name,triplet)
    package_commands.append(command)

    #print(package)
#print(package_commands)
strout = "./vcpkg install %s" % (" ".join(package_commands))
print(strout)
with open("vcpkgcmd.txt", "w", encoding="utf-8-sig") as f:
    f.write(strout)

