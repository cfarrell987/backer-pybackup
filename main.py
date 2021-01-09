import getpass
import os
import glob
import logging
import subprocess
from pathlib import Path
from os.path import expanduser
import tarfile
import shutil
from datetime import date
# TODO Logging
# TODO json or cfg to define paths and variable switches such as logging.
# DONE create function that uploads logs tar to CDN (Private folder)
# TODO in soon-to-be-made config file, add option to change destination and share type i.e NFS, SMB, FTP etc.

### Defines the paths needed ###

# Path to the logs folder
pLogs = "/var/log/"

# Gobbing all the sub directories together to collect them all in one place
p_sys_logs = glob.glob(pLogs + "*")

# this directory is where the compressed System logs and python logs will be stored
p_stage_dir = str(Path.home()) + '/staging'

# Define today
today = date.today()

# Define the file name for the tar-ball of logs
compressed_logs_name = "/logs-backup" + today.strftime("%b-%d-%Y") + ".tar.gz"

# Define the upload destination for the tar-ball
upload_dest = "/mnt/samba/"


# This function gets the system logs paths and stores them in a dict to be used later on.
# It also creates the staging directory for the script in.
def get_sys_logs():
    get_sys_logs = p_sys_logs
    get_stage_dir = p_stage_dir
    index_list_array = []

# Checks if the Staging directory doesn't exist, I know this is backwards but like, deal with it
    if bool(os.path.exists(get_stage_dir)) != True:

        # Try/Catch because Errors
        try:
            os.mkdir(get_stage_dir)
        except OSError:
            print("Creation of Directory %s failed" % get_stage_dir)
        else:
            print("Created Temporary directory %s " % get_stage_dir)
    # Success print if the dir already exists
    else:
        print("Success! " + "Directory: " + "'" + get_stage_dir + "'" + " Exists!")

    # Writes each directory to the index_list_array dict
    for item in get_sys_logs:
        index_list_array.append(item)
        index_file = open(get_stage_dir + "/index.txt", "a")
        index_file.writelines("%s\n" % line for line in index_list_array)


# Packages and compresses the System Logs and stores the tar.gz in the staging folder
def compress_logs():
    getp_sys_logs = p_sys_logs
    getindex_list_array = getp_sys_logs
    getcompressed_logs_name = compressed_logs_name
    tar = tarfile.open(p_stage_dir + compressed_logs_name, "w:gz")
    for item in getindex_list_array:
        print("  Adding %s..." % item)
        tar.add(item, os.path.basename(item))
    tar.close()


def upload_logs():
    if bool(os.path.exists(os.path.join(upload_dest, "Private"))) != True:
        print(os.path.join(upload_dest + "Private"))
        #subprocess.run("mount", "-t", "cifs", "-o", "credentials=/$HOME/creds/smb.creds", "//192.168.2.225/D", "/mnt/samba" )
    else:
        shutil.copyfile(p_stage_dir + compressed_logs_name, upload_dest + os.path.join("Private/" + compressed_logs_name))
        print("Success! " + "logs backed up!")

def clean_staging():
    print("Cleaning all data from staging directory")
    try:
        os.remove(p_stage_dir + compressed_logs_name)
        print("tar ball deleted!")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass
    try:
        os.remove(p_stage_dir + "/index.txt")
        print("index deleted!")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass

# Welcomes the current user as the script starts
def print_welcome(name):
    print(f'Hi, {name}')


# Main Method
if __name__ == '__main__':
    print_welcome(getpass.getuser())
    get_sys_logs()
    #compress_logs()
    #upload_logs()
    clean_staging()
