# backer-pybackup
Python Script to store gzipped Logfiles in an external samba share.

SETUP:
For Security I discourage running the script as sudo as it is accessing network resources. Depending on your configuration this may be acceptable however, most should follow the following:
1. Give your User or UserGroup access to the /var/logs folder `usermod -aG adm <USER>`
2. Mount your share to a folder that does not require sudo access such as in your $HOME directory. 
  a. I reccomend setting up your share to mount on startup in your fstab!
