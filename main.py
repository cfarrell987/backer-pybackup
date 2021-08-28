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

# TODO change logging init to check for logs path instead of the bool
# TODO implement feature to allow user to connect to share whilst script is running, (make it run in a subprocess!!)


today = date.today()

# Define the file name for the tar-ball of logs
compressed_logs_name = "logs-backup" + today.strftime("%b-%d-%Y") + ".tar.gz"


#initialize a config parser for the init file
#rename file to config.json?
def cfgparse():

    config_file = 'init.INI'
    
    config = configparser.ConfigParser()
    config.sections()
    config.read('init.INI')
    config.sections()
   
    return config


def initialize_logging(log_bool, stg_path):
    staging_path = stg_path
    logging_bool = log_bool
    curr_path = os.path.dirname(os.path.realpath(__file__))
    logging_path = os.path.join(str(curr_path), 'logs')
    
    if logging_bool is True:
        print("Initializing Logging...")
        if bool(os.path.exists(logging_path)) is not True:
            try:
                os.mkdir(logging_path)
                print("Logs Directory Created!")
            except OSError:
                print(f'Cannot create Logs directory at %s' % logging_path)
                
    else:
        print("Logging is off!")
    if os.path.exists(logging_path):
        if os.path.exists(os.path.join(logging_path, time.strftime("%Y-%m-%d") +
                '.log')):
            print(os.path.join(logging_path, time.strftime("%Y-%m-%d") + ".log"))
            os.remove(os.path.join(logging_path, time.strftime("%Y-%m-%d") + '.log'))
            
        logging.basicConfig(format='%(asctime)s %(message)s', 
                datefmt='/%m/%d/%Y %I:%M:%S %p', filename=os.path.join(logging_path, 
                 time.strftime("%Y-%m-%d") + '.log'), level=logging.DEBUG)

        print("Complete!")
    else:
        print("An error has occurred initializing logging and has been forced off.")


def make_staging(stg_path):
    staging_path = stg_path
    if os.path.exists(staging_path) is not True:
        # Try/Catch because Errors
        try:
            os.mkdir(staging_path)
        except OSError:
            print("Error: " "Creation of Directory %s failed" % 
                staging_path)
        else:
            print("Created Temporary directory %s " % staging_path)
    # Success print if the dir already exists
    else:
        print("Success! " + "Directory: " + "'" + staging_path + "'" + 
            "Exists!")


# Index system logfiles into a single index file
# Maybe create a db and check if a logfile has been updated since the last upload?!
def index_sys_logs(cfg, stg_path, p_logs):
    cfg = cfg
    index_bool = cfg.getboolean('OPTIONS', 'index')
    staging_path = stg_path
    p_sys_logs = p_logs
    index_list_array = []

    if index_bool is True and os.path.exists(staging_path) is True:
    # Writes each directory to the index_list_array dict
        for item in p_sys_logs:
            index_list_array.append(item)
            index_file = open(os.path.join(staging_path, "index.txt"), "a")
            index_file.writelines("%s\n" % line for line in index_list_array)
        index_file.close()
    else:
        logging.warning("Index Logging is off!")



# Packages and compresses System Logs, stores the tar.gz in the staging folder
def compress_logs(stg_path, p_logs):
    staging_path = stg_path
    p_sys_logs = p_logs

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


def upload_logs(upld_path):
    upload_dest = upld_path
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


def clean_staging(stg_path):
    staging_path = stg_path
    logging.info("Cleaning all data from staging directory")
    try:
        os.remove(os.path.join(staging_path, compressed_logs_name))
        logging.info("tar ball deleted!")
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass
    try:
        os.remove(os.path.join(staging_path, "index.txt"))
        logging.info("index deleted!")
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))
    else:
        pass



#Gets the current logged in user
#This is required as if the script is run with sudo
#the ~ will be set to super user by default
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
            return pwd.getpwuid(pkexec_uid).pw_name
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
    try:
        get_logged_user()
        get_home_path()
        
        config = cfgparse()

        staging_path = str(get_home_path()) + config['PATHS']['staging_path']

        make_staging(staging_path)
        initialize_logging(config.getboolean('OPTIONS', 'logging'), staging_path)
        
        
        sys_logs_path = config['PATHS']['logs_path']    
        p_sys_logs = glob.glob(str(config['PATHS']['logs_path']) + "/*", recursive=True)
            
        index_sys_logs(config, staging_path, p_sys_logs)
        compress_logs(staging_path, p_sys_logs)
        upload_logs(config['PATHS']['upload_destination_path'])

    finally:
        clean_staging(staging_path)
