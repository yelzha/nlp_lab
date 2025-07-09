#!/bin/bash

MODEL=$1 # gpt-35-turbo, gpt-4, llama2
QTYPE=$2 # mmlu, math, chess, human-eval, gsm
DTYPE=$3 # clean, aeda, typo
PART_START=$4
PART_END=$5
SUBSET_NUM=$6

TEMPERATURE=$7 # 0.3 0.7
TOP_P=$8 # 0.95,0.9

K_VALUES=(1 5 10 15 20 25 30 35 40 45 50)

cd ../src
for (( PART=PART_START; PART<PART_END; PART++ ))
do
    echo "Running part $PART..."
    python main.py "$PART" "$SUBSET_NUM" "$MODEL" "$DTYPE" "$QTYPE" "$TEMPERATURE" "$TOP_P"
done

for AGENT in "${K_VALUES[@]}"
do
    echo "AGENT ${AGENT}: All done, evaluating..."
    DIR_NAME="${SLURM_JOB_ID}/log_${QTYPE}_${DTYPE}_${AGENT}_agents"
    python evaluation.py ${DIR_NAME} ${QTYPE}
    echo "AGENT ${AGENT}: All done, evaluating finished..."
done

