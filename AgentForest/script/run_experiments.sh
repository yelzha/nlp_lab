#!/bin/bash

MODEL="qwen3:4b" # qwen3:0.6b
# mistral:7b-instruct-v0.3 llama3:8b-instruct
# gemma:4b gemma:12b
# qwen3:4b qwen3:14b
export VLLM_MODEL_NAME="Qwen/Qwen3-4B"

QTYPE="gsm" # mmlu, math, chess, human-eval, gsm

AGENT_COUNTS=(1 5) # (1 5 10 15 20 25 30 35 40 45 50)
DTYPES=("clean") # clean, aeda, typo

# Loop through each agent count and run the main script
for AGENT in "${AGENT_COUNTS[@]}"
do
    echo "============================================================="
    echo "Running with $AGENT agents on $QTYPE using $MODEL for $DTYPES"
    echo "============================================================="

    sh run_reasoning_task.sh "$AGENT" 1 100 "$MODEL" "$QTYPE" "$DTYPES"

    echo "============================================================="
    echo "========================+Finished+==========================="
    echo "============================================================="
done
