#!/bin/bash

MODEL="qwen3:4b" #
# mistral:7b-instruct-v0.3 llama3:8b-instruct
# gemma:4b gemma:12b
# qwen3:4b qwen3:14b
export VLLM_MODEL_NAME="Qwen/Qwen3-4B"

QTYPE="gsm" # mmlu, math, chess, human-eval, gsm

AGENT_COUNTS=(1 5) # (1 5 10 15 20 25 30 35 40 45 50)

# Loop through each agent count and run the main script
for AGENT in "${AGENT_COUNTS[@]}"
do
    echo "============================================================="
    echo "Running with $AGENT agents on $QTYPE using $MODEL for $DTYPES"
    echo "============================================================="

    #!/bin/bash

    PART_NUM=14
    SUBSET_NUM=100

    TEMPERATURE=1 # 0.3 0.7
    TOP_P=1 # 0.95,0.9

    DTYPE="clean" # clean, aeda, typo

    cd ../src
    DIR_NAME="${SLURM_JOB_ID}/log_${QTYPE}_${DTYPE}_${AGENT}_agents"
    for (( PART=0; PART<PART_NUM; PART++ ))
    do
        EXP_NAME="${QTYPE}_${AGENT}_agents_part_${PART}"
        echo "Running part $PART..."
        python main.py "$PART" "$SUBSET_NUM" "$EXP_NAME" "$MODEL" "$DTYPE" "$DIR_NAME" "$AGENT" "$QTYPE" "$TEMPERATURE" "$TOP_P"
    done
    echo "AGENT ${AGENT}: All done, evaluating..."


    echo "============================================================="
    echo "========================+Finished+==========================="
    echo "============================================================="
done
