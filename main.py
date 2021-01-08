import getpass
import os
import glob
import logging
from subprocess import Popen, PIPE, STDOUT, call
from pathlib import Path
from os.path import expanduser
import tarfile


pLogs = "/var/log/"
pSysLogs = glob.glob(pLogs + "*")
pStageDir = str(Path.home()) + '/tmp'


def getSysLogs():
    getpSysLogs =pSysLogs
    getpStageDir = pStageDir
    indexListArray = []

    if bool(os.path.exists(getpStageDir)) != True:

        try:
            os.mkdir(getpStageDir)
        except OSError:
            print("Creation of Directory %s failed" % getpStageDir)
        else:
            print("Created Temporary directory %s " % getpStageDir)

    else:
        print("Success! " + "Directory: " + "'" + getpStageDir + "'" + " Exists!")

    for item in getpSysLogs:
        #print(item)
        indexListArray.append(item)
        indexFile = open(getpStageDir + "/index.txt", "a")
        #print(indexListArray)
        indexFile.writelines("%s\n" % line for line in indexListArray)


def compress_logs ():
    getpSysLogs = pSysLogs
    getindexListArray = getpSysLogs
    tar = tarfile.open(pStageDir + "/logs-backup.tar.gz", "w:gz")
    for item in getindexListArray:
        print("  Adding %s..." % item)
        tar.add(item, os.path.basename(item))
    tar.close()

def print_welcome(name):
    print(f'Hi, {name}')



if __name__ == '__main__':
    print_welcome(getpass.getuser())
    getSysLogs()
    compress_logs()