
import getpass
import os
import glob
import logging
from pathlib import Path
import tarfile
import shutil
from datetime import date
import time
import configparser

# TODO in soon-to-be-made config file, add option to change destination and share type i.e NFS, SMB, FTP etc.
# TODO create a function to identify the share type, ensure it is active and ensure it can write to the share before
#  attempting to run script
# TODO Add function to prompt user for share, user and pass


# Define today
today = date.today()

# Define the file name for the tar-ball of logs
compressed_logs_name = "/logs-backup" + today.strftime("%b-%d-%Y") + ".tar.gz"


def cfgparse():
    # Define path to system logs
    global logsPath
    # this directory is where the compressed System logs and python logs will be stored
    global stagingPath
    # Define the upload destination for the tar-ball
    global upload_dest
    # Gobbing all the sub directories together to collect them all in one place
    global p_sys_logs
    #Toggle for logging
    global logging_bool
    #Toggle for indexing logs
    global index_bool

    #Define what type of share is being used
    global share_type
    
    config = configparser.ConfigParser()
    config.sections()
    config.read('init.INI')
    config.sections()

    logsPath = config['PATHS']['logsPath']
    stagingPath = str(Path.home()) + config['PATHS']['stagingPath']
    upload_dest = config['PATHS']['uploadDestinationPath']
    p_sys_logs = glob.glob(str(logsPath) + "/*", recursive=True)
    logging_bool = config.getboolean('OPTIONS', 'logging')
    index_bool = config.getboolean('OPTIONS', 'index')
    share_type = config['OPTIONS']['share']

    print(share_type)
def logger():
    curr_path = os.path.dirname(os.path.realpath(__file__))
    loggingPath = str(curr_path) + '/logs'

    if logging_bool is True:
        if bool(os.path.exists(loggingPath)) is not True:
            try:
                os.mkdir(loggingPath)
                print("Logs Directory Created!")
            except OSError:
                print(f'Cannot create Logs directory at %s' % loggingPath )
        print("Initializing Logging...")
        if os.path.exists(stagingPath + time.strftime("/%Y-%m-%d") + 'logs.log'):
            os.remove(stagingPath + time.strftime("/%Y-%m-%d") + 'logs.log')
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='\%m/%d/%Y %I:%M:%S %p', filename= loggingPath +
                                                                                                        time.strftime(
                                                                                                            "/%Y-%m-%d") + 'logs.log',
                            level=logging.DEBUG)
        print("Complete! ")
    else:
        logging.warning('Logging is Off.')


# This function gets the system logs paths and stores them in a dict to be used later on.
# It also creates the staging directory for the script in.
def get_sys_logs():
    index_list_array = []

    if bool(os.path.exists(stagingPath)) is not True:

        # Try/Catch because Errors
        try:
            os.mkdir(stagingPath)
        except OSError:
            logging.error("Error: " "Creation of Directory %s failed" % stagingPath)
        else:
            logging.info("Created Temporary directory %s " % stagingPath)
    # Success print if the dir already exists
    else:
        logging.info("Success! " + "Directory: " + "'" + stagingPath + "'" + " Exists!")

    if index_bool is not True:
        logging.warning("Index Logging is off!")
    # Writes each directory to the index_list_array dict
    else:
        for item in p_sys_logs:
            index_list_array.append(item)
            index_file = open(stagingPath + "/index.txt", "a")
            index_file.writelines("%s\n" % line for line in index_list_array)


# Packages and compresses the System Logs and stores the tar.gz in the staging folder
def compress_logs():
    tar = tarfile.open(stagingPath + compressed_logs_name, "w:gz")
    for item in p_sys_logs:
        print("  Adding %s..." % item)
        tar.add(item, os.path.basename(item))
    tar.close()


def upload_logs():
    if bool(os.path.exists(os.path.join(upload_dest))) is not True:
        print(os.path.join(upload_dest))
        # subprocess.run("mount", "-t", "cifs", "-o", "credentials=/$HOME/creds/smb.creds", "//192.168.2.225/D",
        # "/mnt/samba" )
    else:
        shutil.copyfile(stagingPath + compressed_logs_name,
                        upload_dest + os.path.join(compressed_logs_name))
        logging.info("Success! " + "logs backed up to: " + upload_dest)


def clean_staging():
    logging.info("Cleaning all data from staging directory")
    try:
        os.remove(stagingPath + compressed_logs_name)
        logging.info("tar ball deleted!")
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass
    try:
        os.remove(stagingPath + "/index.txt")
        logging.info("index deleted!")
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass


# Welcomes the current user as the script starts
def print_welcome(name):
    print(f'Hi, {name}')


# Main Method
if __name__ == '__main__':
    print_welcome(getpass.getuser())
    cfgparse()
    logger()
    get_sys_logs()
    compress_logs()
    upload_logs()
    clean_staging()
