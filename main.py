import getpass
import os
import pwd
import subprocess
import glob
import logging
from pathlib import Path
import tarfile
import shutil
from datetime import date
import time
import configparser

# TODO in soon-to-be-made config file, add option to change destination and
# share type i.e NFS, SMB, FTP etc.
# TODO create a function to identify the share type, ensure it is active and
# ensure it can write to the share before
# attempting to run script
# TODO Add function to prompt user for share, user and pass


# Define today
today = date.today()

# Define the file name for the tar-ball of logs
compressed_logs_name = "logs-backup" + today.strftime("%b-%d-%Y") + ".tar.gz"


def cfgparse():
    # Define path to system logs
    global logs_path
    # this directory is where the compressed System logs and python
    # logs will be stored
    global staging_path
    # Define the upload destination for the tar-ball
    global upload_dest
    # Gobbing all the sub directories together to collect them all in one place
    global p_sys_logs
    #Toggle for logging
    global logging_bool
    #Toggle for indexing logs
    global index_bool

    config = configparser.ConfigParser()
    config.sections()
    config.read('init.INI')
    config.sections()

    logs_path = config['PATHS']['logs_path']
    staging_path = str(get_home_path()) + config['PATHS']['staging_path']
    upload_dest = config['PATHS']['upload_destination_path']
    p_sys_logs = glob.glob(str(logs_path) + "/*", recursive=True)
    logging_bool = config.getboolean('OPTIONS', 'logging')
    index_bool = config.getboolean('OPTIONS', 'index')


def initialize_logging():
    curr_path = os.path.dirname(os.path.realpath(__file__))
    logging_path = str(curr_path) + '/logs'

    if logging_bool is True:
        if bool(os.path.exists(logging_path)) is not True:
            try:
                os.mkdir(logging_path)
                print("Logs Directory Created!")
            except OSError:
                print(f'Cannot create Logs directory at %s' % logging_path)
        print("Initializing Logging...")
        if os.path.exists(staging_path + time.strftime("/%Y-%m-%d") +
                'logs.log'):
            os.remove(staging_path + time.strftime("/%Y-%m-%d") + 'logs.log')
        logging.basicConfig(format='%(asctime)s %(message)s', 
                datefmt='\%m/%d/%Y %I:%M:%S %p', filename=logging_path 
                + time.strftime("/%Y-%m-%d") + 'logs.log', level=logging.DEBUG)

        print("Complete! ")
    else:
        logging.warning('Logging is Off.')


# This function gets the system logs paths and stores them to be used later on.
# It also creates the staging directory for the script in.
def get_sys_logs():
    index_list_array = []

    if bool(os.path.exists(staging_path)) is not True:

        # Try/Catch because Errors
        try:
            os.mkdir(staging_path)
        except OSError:
            logging.error("Error: " "Creation of Directory %s failed" % 
                staging_path)
        else:
            logging.info("Created Temporary directory %s " % staging_path)
    # Success print if the dir already exists
    else:
        logging.info("Success! " + "Directory: " + "'" + staging_path + "'" + 
            "Exists!")

    if index_bool is not True:
        logging.warning("Index Logging is off!")
    # Writes each directory to the index_list_array dict
    else:
        for item in p_sys_logs:
            index_list_array.append(item)
            index_file = open(staging_path + "/index.txt", "a")
            index_file.writelines("%s\n" % line for line in index_list_array)


# Packages and compresses System Logs, stores the tar.gz in the staging folder
def compress_logs():
    try:
        print(os.path.join(staging_path, compressed_logs_name))
        tar = tarfile.open(os.path.join(staging_path, compressed_logs_name), "w:gz")
    except:
        logging.error("ERROR: failed to open tarfile!")
    finally:
        for item in p_sys_logs:
            print("  Adding %s..." % item)
            tar.add(item, os.path.basename(item))
        tar.close()


def upload_logs():
    if bool(os.path.exists(os.path.join(upload_dest))) is not True:
        print(os.path.join(upload_dest))
        logging.error("Share is Not Mounted! Please mount share & try again!")
    else:
        logging.info("Share Mounted!")
    try:
        shutil.copyfile(os.path.join(staging_path, compressed_logs_name),
                        os.path.join(upload_dest, compressed_logs_name))
        logging.info("Success! " + "logs backed up to: " + upload_dest)
    except:
        logging.error('Error: CANNOT COPY FILES!')
    else:
        pass


def clean_staging():
    logging.info("Cleaning all data from staging directory")
    try:
       # os.remove(staging_path + compressed_logs_name)
        print(staging_path)
       # logging.info("tar ball deleted!")
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass
    try:
        os.remove(staging_path + "/index.txt")
        logging.info("index deleted!")
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass



#Gets the current logged in user
#This is required as if the script is run with sudo
#the ~ will be set to sudo
def get_logged_user():

    try:
        return os.getlogin()
    except:
        pass

    try:
        user = os.environ['USER']
    except KeyError:
        return getpass.getuser()

    if user == 'root':
        try:
            return os.environ['SUDO_USER']
        except KeyError:
            pass

        try:
            pkexec_uid = int(os.environ['PKEXEC_UID'])
            return owd.getpwuid(pkexec_uid).pw_name
        except KeyError:
            pass
    return user

#Sets home_dir to whatever the logged in users home path is
#Needs to be done this way in case a user decides to 
#change their ~ to anything other than /home/$USER
#should also allow portability with MacOS
def get_home_path():
    home_dir = pwd.getpwnam(get_logged_user()).pw_dir
    return home_dir


# Main Method
if __name__ == '__main__':

    get_logged_user()
    get_home_path()
    cfgparse()
    initialize_logging()
    get_sys_logs()
    compress_logs()
    upload_logs()
    clean_staging()
