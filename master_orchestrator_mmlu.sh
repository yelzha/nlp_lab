#!/bin/bash
# master_orchestrator_.sh

MODELS=("Qwen3-4B" "Qwen3-14B" "Llama-3.1-8B-Instruct" "Mistral-7B-Instruct-v0.3")
QTYPES=("mmlu")
DTYPES=("clean" "punctuation_10" "punctuation_30" "punctuation_50" "wikitypo")
SUBSET_NUMS=(100)
TEMPERATURES=(1)
TOP_PS=(1)
VLLM_MODEL_NAMES=("Qwen/Qwen3-4B" "Qwen/Qwen3-14B" "meta-llama/Llama-3.1-8B-Instruct" "mistralai/Mistral-7B-Instruct-v0.3")
DEBUGS=("False")
COMMON_STAGES="0 2;2 4;4 6;6 8;8 10;10 12"


ORCHESTRATOR_SCRIPT="./orchestrator_single_experiment.sh" # This is the script causing the permission denied
if [ ! -f "$ORCHESTRATOR_SCRIPT" ]; then
    echo "Error: orchestrator.sh not found at $ORCHESTRATOR_SCRIPT."
    echo "Please ensure 'orchestrator.sh' is in the same directory or provide its full path."
    exit 1
fi
# Remove or comment out this check as we will explicitly call bash
# if [ ! -x "$ORCHESTRATOR_SCRIPT" ]; then
#     echo "Error: orchestrator.sh is not executable. Please run 'chmod +x $ORCHESTRATOR_SCRIPT'."
#     exit 1
# fi

# Initialize the last job ID. The first orchestrator.sh run will have no external dependency.
LAST_SLURM_ID=""

# --- Iterate through all combinations of parameters ---
for MODEL in "${MODELS[@]}"; do
    for QTYPE in "${QTYPES[@]}"; do
        for DTYPES in "${DTYPES[@]}"; do
            for SUBSET_NUM in "${SUBSET_NUMS[@]}"; do
                for TEMPERATURE in "${TEMPERATURES[@]}"; do
                    for TOP_P in "${TOP_PS[@]}"; do
                        for VLLM_MODEL_NAME in "${VLLM_MODEL_NAMES[@]}"; do
                            for DEBUG in "${DEBUGS[@]}"; do
                                # Construct the command to run orchestrator.sh with current parameters
                                # Explicitly call bash to run the script
                                RUN_CMD="bash \"$ORCHESTRATOR_SCRIPT\"" # <--- THIS IS THE CRUCIAL CHANGE
                                RUN_CMD+=" \"$MODEL\""
                                RUN_CMD+=" \"$QTYPE\""
                                RUN_CMD+=" \"$DTYPES\""
                                RUN_CMD+=" \"$SUBSET_NUM\""
                                RUN_CMD+=" \"$TEMPERATURE\""
                                RUN_CMD+=" \"$TOP_P\""
                                RUN_CMD+=" \"$VLLM_MODEL_NAME\""
                                RUN_CMD+=" \"$DEBUG\""
                                RUN_CMD+=" \"$COMMON_STAGES\"" # Pass the stages string

                                # If there's a previous SLURM job ID, add it as a dependency
                                if [ -n "$LAST_SLURM_ID" ]; then
                                    RUN_CMD+=" \"$LAST_SLURM_ID\""
                                fi

                                # Execute orchestrator.sh and capture its output (the last SLURM job ID from its run)
                                NEW_SLURM_ID=$(eval "$RUN_CMD")

                                # Clean up the captured ID (remove any leading/trailing whitespace)
                                NEW_SLURM_ID=$(echo "$NEW_SLURM_ID" | tr -d '[:space:]')

                                if [ -n "$NEW_SLURM_ID" ]; then
                                    LAST_SLURM_ID="$NEW_SLURM_ID" # Update the last ID for the next iteration
                                else
                                    # If orchestrator.sh failed or didn't return an ID, reset LAST_SLURM_ID
                                    # This prevents subsequent runs from depending on a non-existent job.
                                    LAST_SLURM_ID=""
                                    echo "Warning: orchestrator.sh for MODEL=$MODEL, QTYPE=$QTYPE, DTYPES=$DTYPES failed or returned no Job ID. Subsequent runs will not have a dependency from this one."
                                fi
                            done
                        done
                    done
                done
            done
        done
    done
done

echo "Master Orchestration Script finished."
if [ -n "$LAST_SLURM_ID" ]; then
    echo "The very last SLURM Job ID submitted in this entire sequence was: $LAST_SLURM_ID"
else
    echo "No SLURM Job IDs were successfully captured throughout the entire sequence."
fi