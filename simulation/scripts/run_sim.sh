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

    echo $ENV_FILE
    echo $LOG_FILE

    make run_kubernetes ENV_FILE=$ENV_FILE
    echo "SLEEPING"
    sleep $SIM_TIME
    echo "ENDING SIMULATION"
    make clean
    echo "AGGREGATING LOGS"
    make aggregate_logs LOG_FILE=$LOG_FILE ENV_FILE=$ENV_FILE SIM_TIME=$SIM_TIME DOWN_TIME=$DOWN_TIME LOG_DIR_LOCAL=$LOG_DIR
}

echo $SIM_FOLDER $SIM_TIME
for scenario in "${SCENARIOS[@]}"
do
    echo "RUNNING $scenario"
    run_simulation $scenario
done

exit

