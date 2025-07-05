#!/bin/bash

MODEL="opt-125m" # qwen3:0.6b
# mistral:7b-instruct-v0.3 llama3:8b-instruct
# gemma:4b gemma:12b
# qwen3:4b qwen3:14b
export VLLM_MODEL_NAME="facebook/opt-125m"

QTYPE="gsm" # mmlu, math, chess, human-eval, gsm

AGENT_COUNTS=(1 5) # (1 5 10 15 20 25 30 35 40 45 50)
DTYPES=("clean") # clean, aeda, typo

# Loop through each agent count and run the main script
for AGENT in "${AGENT_COUNTS[@]}"
do
    echo "============================================================="
    echo "Running with $AGENT agents on $QTYPE using $MODEL for $DTYPES"
    echo "============================================================="

    #!/bin/bash

    PART_NUM=1
    SUBSET_NUM=100

    TEMPERATURE=1 # 0.3 0.7
    TOP_P=1 # 0.95,0.9

    cd ../src
    DIR_NAME="${SLURM_JOB_ID}/log_${QTYPE}_${DTYPE}_${AGENT}_agents"
    for (( PART=0; PART<PART_NUM; PART++ ))
    do
        EXP_NAME="${QTYPE}_${AGENT}_agents_part_${PART}"
        echo "Running part $PART..."
        python3.11 main.py "$PART" "$SUBSET_NUM" "$EXP_NAME" "$MODEL" "$DTYPE" "$DIR_NAME" "$AGENT" "$QTYPE" "$TEMPERATURE" "$TOP_P" &
    done
    wait
    echo "AGENT ${AGENT}: All done, evaluating..."


    echo "============================================================="
    echo "========================+Finished+==========================="
    echo "============================================================="
done
