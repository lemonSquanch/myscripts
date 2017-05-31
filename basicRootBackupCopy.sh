#!/bin/bash

echo "Usage: # <$0> <path to save to>";

if [[ $(id -u) -ne 0 ]];
then
    echo "Please run as root..";
    exit -1;
fi

tar -c --use-compress-program=pigz --exclude="/var/log" --exclude="/usr/tools/*" --exclude="/home/*" --exclude="/dev/*" --exclude="/proc/*" --exclude="/sys/*" --exclude="/tmp/*" --exclude="/run/*" --exclude="/mnt/*" --exclude="/media/*" --exclude="/lost+found" -f "$1/root_backup.tar.gz" /;

