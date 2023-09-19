#!/bin/bash

set -e

SIM_FOLDER=$1
SIM_TIME=$2
DOWN_TIME=$3
SCENARIOS=($(ls $SIM_FOLDER/scenarios))

# Check if we should log to file or not
if [ -n "$4" ]
  then
    $LOG_TO_FILE=">> $4"
fi



function run_simulation() {
    scenario=$1
    ENV_FILE=$SIM_FOLDER/scenarios/$scenario
    LOG_FILE=$SIM_FOLDER/results/$(basename $scenario .properties).json

    echo $ENV_FILE $LOG_TO_FILE
    echo $LOG_FILE $LOG_TO_FILE

    make run_kubernetes ENV_FILE=$ENV_FILE $LOG_TO_FILE 2>&1
    echo "SLEEPING" $LOG_TO_FILE
    sleep $SIM_TIME
    echo "ENDING SIMULATION"  $LOG_TO_FILE
    make clean  $LOG_TO_FILE 2>&1
    echo "AGGREGATING LOGS" $LOG_TO_FILE
    make aggregate_logs LOG_FILE=$LOG_FILE ENV_FILE=$ENV_FILE SIM_TIME=$SIM_TIME DOWN_TIME=$DOWN_TIME $LOG_TO_FILE 2>&1
}

echo $SIM_FOLDER $SIM_TIME $LOG_TO_FILE
for scenario in "${SCENARIOS[@]}"
do
    echo "RUNNING $scenario" $LOG_TO_FILE
    echo $LOG_TO_FILE
    run_simulation $scenario
done

exit

