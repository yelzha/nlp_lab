#!/bin/bash

export LLM_IP="127.0.0.0:11500"

AGENT=$1
MODEL=$2 # gpt-35-turbo, gpt-4, llama2
QTYPE=$3 # mmlu, math, chess, human-eval, gsm
DTYPE=$4 # clean, aeda, typo


if [ "${QTYPE}" = "human-eval" ]; then
    sh run_genration_task.sh $AGENT 1 100 $MODEL
else
    sh run_reasoning_task.sh $AGENT 1 100 $MODEL $QTYPE $DTYPE
fi