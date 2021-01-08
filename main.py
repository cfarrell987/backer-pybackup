import getpass
import os
import glob
import logging
from subprocess import Popen, PIPE, STDOUT, call
from pathlib import Path
from os.path import expanduser
import tarfile

# TODO Logging
# TODO json or cfg to define paths and variable switches such as logging.
# Defines the paths needed
# Path to the logs folder
pLogs = "/var/log/"
# Gobbing all the sub directories together to collect them all in one place
p_sys_logs = glob.glob(pLogs + "*")
# this directory is where the compressed System logs and python logs will be stored
p_stage_dir = str(Path.home()) + '/staging'


# This function gets the system logs paths and stores them in a dict to be used later on.
# It also creates the staging directory for the script in.
def getSysLogs():
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
        # print(item)
        index_list_array.append(item)
        indexFile = open(get_stage_dir + "/index.txt", "a")
        # print(index_list_array)
        indexFile.writelines("%s\n" % line for line in index_list_array)


# Packages and compresses the System Logs and stores the tar.gz in the staging folder
def compress_logs():
    getp_sys_logs = p_sys_logs
    getindex_list_array = getp_sys_logs
    tar = tarfile.open(p_stage_dir + "/logs-backup.tar.gz", "w:gz")
    for item in getindex_list_array:
        print("  Adding %s..." % item)
        tar.add(item, os.path.basename(item))
    tar.close()


# Welcomes the current user as the script starts
def print_welcome(name):
    print(f'Hi, {name}')


# Main Method
if __name__ == '__main__':
    print_welcome(getpass.getuser())
    getSysLogs()
    compress_logs()
