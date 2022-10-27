#!/bin/bash

FILE=$(cat $1)
#echo "$FILE"

for var in "${@:2}"
do
    KEY=$(echo $var | cut -d "=" -f1)
    VALUE=$(echo $var | cut -d "=" -f2)
    #echo $KEY $VALUE

    FILE=$(echo "$FILE" | sed s/{$KEY}/$VALUE/)
done

#echo "$FILE"
echo "$FILE" | kubectl apply -f -