#/usr/bin/env python

from paramiko import SSHClient
from scp import SCPClient
import os
import getpass
import py7zr
import argparse
import subprocess

def sevenZipFolder(folder: str):
    folder = os.path.normpath(folder)
    archive_name = os.path.basename(folder) + ".7z"
    print("7zipping %s into %s" %(folder, archive_name))
    output = subprocess.run(["7z", "a", archive_name, folder])
    return archive_name, output

parser = argparse.ArgumentParser("7z folders and scp the resulting archives to a backup server")
parser.add_argument('folders', metavar='folder', type=str, nargs='+',  help='The folders to back up')
parser.add_argument('--host', type=str, required=True , help="Host to back up the archive to via scp")
parser.add_argument('--username', type=str, required=True ,  help="Username on the backup host")
parser.add_argument('--output_dir', type=str, default="~" ,  help='Directory to put the resulting archives on backup host')
args = parser.parse_args()
argdict = vars(args)
folders = argdict["folders"]
output_dir = argdict["output_dir"]
username = argdict["username"]
host = argdict["host"]
print(folders)
print(output_dir)
password = getpass.getpass(prompt='Enter password for %s on %s: ' % (username,host), stream=None)
ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect(host,username=username,password=password)
ssh.close()
for folder in folders:
    archive_name, zip_output = sevenZipFolder(folder)
    output_archive_name = os.path.join(output_dir,archive_name).replace("\\","/")
    print("uploading %s to %s" %(archive_name, host+":"+output_archive_name))
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(host,username=username,password=password)

    # SCPCLient takes a paramiko transport as an argument
    scp = SCPClient(ssh.get_transport())
    scp.put(archive_name, remote_path=output_dir)
    scp.close()

