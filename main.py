import getpass
import os
import glob
import logging
from subprocess import Popen, PIPE, STDOUT, call
from pathlib import Path
from os.path import expanduser



def getSysLogs():
    pLogs = "/var/log/"
    pSyslogs = glob.glob(pLogs + "*")
    pStageDir =  str(Path.home()) + '/tmp'
    indexListArray = []

    if bool(os.path.exists(pStageDir)) != True:

        try:
            os.mkdir(pStageDir)
        except OSError:
            print("Creation of Directory %s failed" % pStageDir)
        else:
            print("Created Temporary directory %s " % pStageDir)

    else:
        print("Success! " + "Directory: " + "'" + pStageDir + "'" + " Exists!")

    for item in pSyslogs:
        #print(item)
        indexListArray.append(item)
        indexFile = open(pStageDir + "/index.txt", "a")
        #print(indexListArray)
        indexFile.writelines("%s\n" % line for line in indexListArray)


def print_welcome(name):
    print(f'Hi, {name}')



if __name__ == '__main__':
    print_welcome(getpass.getuser())
    getSysLogs()