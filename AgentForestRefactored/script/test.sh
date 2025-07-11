#!/bin/bash

MODEL="qwen3-4B" # gpt-35-turbo, gpt-4, llama2
QTYPE="gsm" # mmlu, math, chess, human-eval, gsm
DTYPE="clean" # clean, aeda, typo

TEMPERATURE=1 # 0.3 0.7
TOP_P=0.95 # 0.95,0.9

K_VALUES=(1 5 10 15 20 25 30 35 40 45 50)
BASE_DIR_NAME="experiments/${DTYPE}/${MODEL}/${QTYPE}"

# for (( AGENT=1; AGENT<51; AGENT++ ))
for AGENT in "${K_VALUES[@]}"
do
    echo "AGENT ${AGENT}: All done, evaluating..."
    DIR_NAME="${BASE_DIR_NAME}/log_${QTYPE}_${DTYPE}_${AGENT}_agents"
    python evaluation.py ${DIR_NAME} ${QTYPE}
    echo "AGENT ${AGENT}: All done, evaluating finished..."
done

