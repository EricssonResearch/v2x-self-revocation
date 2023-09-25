#!/bin/bash

set -e

SIM_FOLDER=$1
SIM_TIME=$2
DOWN_TIME=$3
LOG_DIR=$4
SCENARIOS=($(ls $SIM_FOLDER/scenarios))

function run_simulation() {
    scenario=$1
    ENV_FILE=$SIM_FOLDER/scenarios/$scenario
    LOG_FILE=$SIM_FOLDER/results/$(basename $scenario .properties).json

    if [ $SIM_TIME -eq "-1" ]; then
    SIM_TIME_RUN=`cat $ENV_FILE | grep SIM_TIME | cut -d "=" -f2`
    else
    SIM_TIME_RUN=$SIM_TIME
    fi

    if [ $DOWN_TIME -eq "-1"  ]; then
    DOWN_TIME_RUN=`cat $ENV_FILE | grep DOWN_TIME | cut -d "=" -f2`
    else
    DOWN_TIME_RUN=$DOWN_TIME
    fi

    echo "RUNNING $scenario SIM_TIME: $SIM_TIME_RUN DOWN_TIME: $DOWN_TIME_RUN"
    make run_kubernetes ENV_FILE=$ENV_FILE

    echo "SLEEPING"
    sleep $SIM_TIME_RUN

    echo "ENDING SIMULATION"
    kubectl delete ns v2x

    echo "AGGREGATING LOGS"
    make aggregate_logs LOG_FILE=$LOG_FILE ENV_FILE=$ENV_FILE SIM_TIME=$SIM_TIME_RUN DOWN_TIME=$DOWN_TIME_RUN LOG_DIR_LOCAL=$LOG_DIR

    echo "DELETING LOGS"
    rm -rf logs/*
}

for scenario in "${SCENARIOS[@]}"
do
    run_simulation $scenario
done

echo "ALL DONE"
exit

