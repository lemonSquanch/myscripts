#!/bin/bash


function nascar()
{
     if [ $# -lt 2 ] || ! [[ $1 =~ ^[0-9]+$ ]]; then
         echo "Usage: nascar <cycle count> <command to execute>";
         return;
     fi
 
     i=0;
     while [ $i -lt $1 ]; do
         i=$((i+1));
         ${@:2};
     if [ "$?" -ne "0" ]; then
         echo "Last command(#$i) failed with code: $?";
         return 1;
     else    
         echo "Finished all $i commands! No bad returns!";
     fi
     done
}

nascar "$1" "$2";
