#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo "You need to specify what text to filter and from what file..";
    return;
fi

f="$1"
shift;

blacklist="";
for v in "$@"
do
    blacklist="$v\|$blacklist";
done

cat "$f" | sed "s/$blacklist//g" | sed "/^$/d";
