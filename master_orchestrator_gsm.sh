#!/bin/bash
# master_orchestrator_.sh

MODELS=("gemma-3-4b-it" "gemma-3-12b-it")
DTYPES=("clean" "punctuation_10" "punctuation_30" "punctuation_50" "wikitypo" "r2ata")
VLLM_MODEL_NAMES=("google/gemma-3-4b-it" "google/gemma-3-12b-it")

# Fixed parameters
QTYPE="gsm"
SUBSET_NUM=100
TEMPERATURE=1
TOP_P=1
DEBUG="False"
COMMON_STAGES="0 2;2 4;4 6;6 8;8 10;10 12;12 14"
WORKER_SCRIPT="./scripts/run_experiment_a100.sh"

# Set resume point
RESUME_MODEL=""
RESUME_DTYPE=""
FOUND_START=false

# If no resume point specified, start immediately
if [ -z "$RESUME_MODEL" ] && [ -z "$RESUME_DTYPE" ]; then
  FOUND_START=true
fi

ORCHESTRATOR_SCRIPT="./orchestrator_single_experiment.sh"
if [ ! -f "$ORCHESTRATOR_SCRIPT" ]; then
    echo "Error: orchestrator.sh not found at $ORCHESTRATOR_SCRIPT."
    exit 1
fi

LAST_SLURM_ID=""

# Iterate through all combinations
for MODEL in "${MODELS[@]}"; do
    for DTYPE in "${DTYPES[@]}"; do

        # Skip until the resume point is found
        if [ "$FOUND_START" = false ]; then
          if [[ "$MODEL" == "$RESUME_MODEL" && "$DTYPE" == "$RESUME_DTYPE" ]]; then
            FOUND_START=true
            echo "===> Resuming from MODEL=$MODEL, DTYPE=$DTYPE"
          else
            echo "Skipping MODEL=$MODEL, DTYPE=$DTYPE"
            continue
          fi
        fi


        # Find index of current MODEL
        MODEL_INDEX=-1
        for i in "${!MODELS[@]}"; do
            if [[ "${MODELS[$i]}" == "$MODEL" ]]; then
                MODEL_INDEX="$i"
                break
            fi
        done

        # Ensure corresponding VLLM model name
        if [[ "$MODEL_INDEX" -ne -1 && "$MODEL_INDEX" -lt "${#VLLM_MODEL_NAMES[@]}" ]]; then
            VLLM_MODEL_NAME="${VLLM_MODEL_NAMES[$MODEL_INDEX]}"
        else
            echo "Warning: No corresponding VLLM_MODEL_NAME found for MODEL: $MODEL. Skipping."
            continue
        fi

        # Prepare dependency
        DEPENDENCY_ARG=""
        if [ -n "$LAST_SLURM_ID" ]; then
            DEPENDENCY_ARG="$LAST_SLURM_ID"
        fi

        # Run orchestrator script
        NEW_SLURM_ID=$(bash "$ORCHESTRATOR_SCRIPT" \
            "$MODEL" \
            "$QTYPE" \
            "$DTYPE" \
            "$SUBSET_NUM" \
            "$TEMPERATURE" \
            "$TOP_P" \
            "$VLLM_MODEL_NAME" \
            "$DEBUG" \
            "$COMMON_STAGES" \
            "$DEPENDENCY_ARG" \
            "$WORKER_SCRIPT")

        NEW_SLURM_ID=$(echo "$NEW_SLURM_ID" | tail -n 1 | tr -d '[:space:]')

        if [ -n "$NEW_SLURM_ID" ]; then
            LAST_SLURM_ID="$NEW_SLURM_ID"
            echo "Submitted job with ID: $NEW_SLURM_ID. Dependency for next run: $LAST_SLURM_ID"
        else
            LAST_SLURM_ID=""
            echo "Warning: orchestrator_single_experiment.sh for MODEL=$MODEL, DTYPE=$DTYPE failed or returned no Job ID." >&2
        fi

    done
done

echo "Master Orchestration Script finished."
if [ -n "$LAST_SLURM_ID" ]; then
    echo "The very last SLURM Job ID submitted in this entire sequence was: $LAST_SLURM_ID"
else
    echo "No SLURM Job IDs were successfully captured throughout the entire sequence."
fi
