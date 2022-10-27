#!/bin/bash

RA=$(kubectl -n v2x get pod -l run=ra -o jsonpath="{.items[0].metadata.name}")
ISS=$(kubectl -n v2x get pod -l run=issuer -o jsonpath="{.items[0].metadata.name}")

until kubectl get pods -n v2x $RA -o jsonpath="Name: {.metadata.name} Status: {.status.phase}" | grep Running
do 
    RA=$(kubectl -n v2x get pod -l run=ra -o jsonpath="{.items[0].metadata.name}")
    sleep 1
done

until kubectl get pods -n v2x $ISS -o jsonpath="Name: {.metadata.name} Status: {.status.phase}" | grep Running
do 
    ISS=$(kubectl -n v2x get pod -l run=issuer -o jsonpath="{.items[0].metadata.name}")
    sleep 1
done

echo "Done"