#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Expected arguments: <application> <cpulimit for each instance%>";
    exit 1;
fi

set -e;
echo "cpuLimit monitoring for \"$1\"!";

pids="";
while true; do
    for p1 in `pidof "$1"`; do
        found="0";
        for p2 in ${pids}; do
            if [ "$p2" == "$p1" ]; then
                found="1"; 
            fi
        done
        if [ "$found" == "0" ]; then
            pids="$pids $p1";
            cpulimit -p $p1 -l $2 &
        fi
    done
    echo "PIDLIST: ${pids}";
    sleep 0.1;
done
