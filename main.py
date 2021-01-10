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
import configparser

# TODO Logging
# TODO json or cfg to define paths and variable switches such as logging.
# DONE create function that uploads logs tar to CDN (Private folder)
# TODO in soon-to-be-made config file, add option to change destination and share type i.e NFS, SMB, FTP etc.

### Defines the paths needed ###

# Path to the logs folder
pLogs = "/var/log/"

# Define today
today = date.today()

# Define the file name for the tar-ball of logs
compressed_logs_name = "/logs-backup" + today.strftime("%b-%d-%Y") + ".tar.gz"


def cfgparse():
    global logsPath
    # this directory is where the compressed System logs and python logs will be stored
    global stagingPath
    # Define the upload destination for the tar-ball
    global upload_dest
    # Gobbing all the sub directories together to collect them all in one place
    global p_sys_logs
    # placeholder comment
    global logging_bool
    # placeholder comment
    global index_bool
    config = configparser.ConfigParser()
    config.sections()
    config.read('init.INI')
    config.sections()

    logsPath = config['PATHS']['logsPath']
    stagingPath = str(Path.home()) + config['PATHS']['stagingPath']
    upload_dest = config['PATHS']['uploadDestinationPath']
    p_sys_logs = glob.glob(str(logsPath) + "/*", recursive=True)
    logging_bool = config['OPTIONS']['logging']
    index_bool = config['OPTIONS']['index']

# This function gets the system logs paths and stores them in a dict to be used later on.
# It also creates the staging directory for the script in.
def get_sys_logs():
    index_list_array = []

    # Checks if the Staging directory doesn't exist, I know this is backwards but like, deal with it
    if bool(os.path.exists(stagingPath)) != True:

        # Try/Catch because Errors
        try:
            os.mkdir(stagingPath)
        except OSError:
            print("Creation of Directory %s failed" % stagingPath)
        else:
            print("Created Temporary directory %s " % stagingPath)
    # Success print if the dir already exists
    else:
        print("Success! " + "Directory: " + "'" + stagingPath + "'" + " Exists!")

    # Writes each directory to the index_list_array dict
    if index_bool == "ON":
        for item in p_sys_logs:
            index_list_array.append(item)
            index_file = open(stagingPath + "/index.txt", "a")
            index_file.writelines("%s\n" % line for line in index_list_array)
    else:
        print("Index Logging is OFF")

# Packages and compresses the System Logs and stores the tar.gz in the staging folder
def compress_logs():
    getp_sys_logs = p_sys_logs
    getindex_list_array = getp_sys_logs
    getcompressed_logs_name = compressed_logs_name
    tar = tarfile.open(stagingPath + compressed_logs_name, "w:gz")
    for item in getindex_list_array:
        print("  Adding %s..." % item)
        tar.add(item, os.path.basename(item))
    tar.close()


def upload_logs():
    if bool(os.path.exists(os.path.join(upload_dest, "/Private"))) != True:
        print(os.path.join(upload_dest + "/Private"))
        # subprocess.run("mount", "-t", "cifs", "-o", "credentials=/$HOME/creds/smb.creds", "//192.168.2.225/D",
        # "/mnt/samba" )
    else:
        shutil.copyfile(stagingPath + compressed_logs_name,
                        upload_dest + os.path.join("/Private" + compressed_logs_name))
        print("Success! " + "logs backed up!")


def clean_staging():
    print("Cleaning all data from staging directory")
    try:
        os.remove(stagingPath + compressed_logs_name)
        print("tar ball deleted!")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass
    try:
        os.remove(stagingPath + "/index.txt")
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
    cfgparse()
    get_sys_logs()
    #compress_logs()
    #upload_logs()
    #clean_staging()
