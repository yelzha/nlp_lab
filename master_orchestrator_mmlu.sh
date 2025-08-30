#!/bin/bash
# master_orchestrator_.sh for MMLU

MODELS=("Qwen3-4B" "Qwen3-14B" "Llama-3.1-8B-Instruct" "Mistral-7B-Instruct-v0.3")
DTYPES=("clean" "punctuation_10" "punctuation_30" "punctuation_50" "wikitypo" "r2ata")
VLLM_MODEL_NAMES=("Qwen/Qwen3-4B" "Qwen/Qwen3-14B" "meta-llama/Llama-3.1-8B-Instruct" "mistralai/Mistral-7B-Instruct-v0.3")

# Fixed parameters
QTYPE="mmlu"
SUBSET_NUM=100
TEMPERATURE=1
TOP_P=1
DEBUG="TRUE"
COMMON_STAGES="0 1" # 0 2;2 4;4 6;6 8;8 10;10 12
WORKER_SCRIPT="./scripts/run_experiment_a40.sh"
EXPERIMENT_DIRECTORY="view100"  # experiments
DEPENDENCY="FALSE"

# === RESUME POINT ===
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

# --- Iterate through all combinations of MODEL × DTYPE ---
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

        # Find matching VLLM model by index
        MODEL_INDEX=-1
        for i in "${!MODELS[@]}"; do
            if [[ "${MODELS[$i]}" == "$MODEL" ]]; then
                MODEL_INDEX="$i"
                break
            fi
        done

        if [[ "$MODEL_INDEX" -ne -1 && "$MODEL_INDEX" -lt "${#VLLM_MODEL_NAMES[@]}" ]]; then
            VLLM_MODEL_NAME="${VLLM_MODEL_NAMES[$MODEL_INDEX]}"
        else
            echo "Warning: No VLLM_MODEL_NAME for MODEL: $MODEL. Skipping."
            continue
        fi

        # Handle SLURM dependency if set
        DEPENDENCY_ARG=""
        if [ -n "$LAST_SLURM_ID" ]; then
            DEPENDENCY_ARG="$LAST_SLURM_ID"
        fi

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
            "$WORKER_SCRIPT" \
            "$EXPERIMENT_DIRECTORY" \
            "$DEPENDENCY")

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
