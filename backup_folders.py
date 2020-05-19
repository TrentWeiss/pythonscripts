from paramiko import SSHClient
from scp import SCPClient
import os
import getpass
import py7zr
import argparse
import subprocess

def sevenZipFolder(folder: str):
    archive_name = os.path.basename(folder) + ".7z"
    print("7zipping %s into %s" %(folder, archive_name))
    output = subprocess.run(["7z", "a", archive_name, folder])
    return archive_name

parser = argparse.ArgumentParser("Back up folders and scp it to the CS department's systems")
parser.add_argument('folders', metavar='folder', type=str, nargs='+',  help='The folders to back up')
parser.add_argument('--username', type=str, default="ttw2xk",  help="Username on the CS systems")
parser.add_argument('--host', type=str, default="portal.cs.virginia.edu" , help="Host to scp to")
parser.add_argument('--output_dir', type=str,default="/p/DeepRacing/datasets",  help='Directory to put the resulting archives on the CS backup')
args = parser.parse_args()
folders = args.folders
output_dir = args.output_dir
username = args.username
host = args.host
print(folders)
print(output_dir)
password = getpass.getpass(prompt='Password: ', stream=None)
ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect(host,username=username,password=password)
ssh.close()
for folder in folders:
    archive_name = sevenZipFolder(folder)
    print("uploading %s to %s" %(archive_name, host+":"+os.path.join(output_dir,archive_name)))
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(host,username=username,password=password)

    # SCPCLient takes a paramiko transport as an argument
    scp = SCPClient(ssh.get_transport())
    scp.put(archive_name, remote_path=output_dir)
    scp.close()
