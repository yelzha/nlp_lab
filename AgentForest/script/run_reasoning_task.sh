#!/bin/bash

AGENT=$1
PART_NUM=$2
SUBSET_NUM=$3
MODEL=$4 # gpt-35-turbo, gpt-4, llama2
QTYPE=$5 # mmlu, math, chess, human-eval, gsm
DTYPE=$6 # clean, aeda, typo

TEMPERATURE=1 # 0.3 0.7
TOP_P=1 # 0.95,0.9

cd ../src
DIR_NAME="log_${QTYPE}_${DTYPE}_${AGENT}_agents"
for (( PART=0; PART<PART_NUM; PART++ ))
do
    EXP_NAME="${QTYPE}_${AGENT}_agents_part_${PART}"
    echo "Running part $PART..."
    python main.py "$PART" "$SUBSET_NUM" "$EXP_NAME" "$MODEL" "$DTYPE" "$DIR_NAME" "$AGENT" "$QTYPE" "$TEMPERATURE" "$TOP_P"
done
echo "AGENT ${AGENT}: All done, evaluating..."
python evaluation.py ${DIR_NAME} ${QTYPE}
