#!/bin/bash
# master_orchestrator_math.sh  (assuming this is the file that's throwing the error)

MODELS=("Qwen3-4B" "Qwen3-14B" "Llama-3.1-8B-Instruct" "Mistral-7B-Instruct-v0.3")
QTYPES=("math")
DTYPES=("clean" "punctuation_10" "punctuation_30" "punctuation_50" "wikitypo")
SUBSET_NUMS=(100)
TEMPERATURES=(1)
TOP_PS=(1)
VLLM_MODEL_NAMES=("Qwen/Qwen3-4B" "Qwen/Qwen3-14B" "meta-llama/Llama-3.1-8B-Instruct" "mistralai/Mistral-7B-Instruct-v0.3")
DEBUGS=("False")
COMMON_STAGES="0 1"


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
                        # Iterate through VLLM_MODEL_NAMES. Ensure this aligns with MODELS if it's 1-to-1
                        # If VLLM_MODEL_NAMES and MODELS have different lengths or order, you might need
                        # a different mapping strategy (e.g., an associative array or a manual mapping).
                        # For now, assuming they align by index for simplicity.
                        # This loop needs careful consideration if MODELS and VLLM_MODEL_NAMES don't have a 1:1 direct mapping by index.
                        # Let's adjust this to iterate VLLM_MODEL_NAMES by index of MODELS.
                        # Find the index of the current MODEL in MODELS array
                        MODEL_INDEX=-1
                        for i in "${!MODELS[@]}"; do
                            if [[ "${MODELS[$i]}" == "$MODEL" ]]; then
                                MODEL_INDEX="$i"
                                break
                            fi
                        done

                        # If a corresponding VLLM_MODEL_NAME is found
                        if [[ "$MODEL_INDEX" -ne -1 && "$MODEL_INDEX" -lt "${#VLLM_MODEL_NAMES[@]}" ]]; then
                            VLLM_MODEL_NAME="${VLLM_MODEL_NAMES[$MODEL_INDEX]}"
                        else
                            echo "Warning: No corresponding VLLM_MODEL_NAME found for MODEL: $MODEL. Skipping this combination."
                            continue # Skip to the next MODEL iteration
                        fi

                        for DEBUG in "${DEBUGS[@]}"; do
                            # Directly call bash with the script and its arguments
                            # Make sure LAST_SLURM_ID is only passed if it's not empty, otherwise pass an empty string
                            DEPENDENCY_ARG=""
                            if [ -n "$LAST_SLURM_ID" ]; then
                                DEPENDENCY_ARG="$LAST_SLURM_ID"
                            fi

                            NEW_SLURM_ID=$(bash "$ORCHESTRATOR_SCRIPT" \
                                "$MODEL" \
                                "$QTYPE" \
                                "$DTYPES" \
                                "$SUBSET_NUM" \
                                "$TEMPERATURE" \
                                "$TOP_P" \
                                "$VLLM_MODEL_NAME" \
                                "$DEBUG" \
                                "$COMMON_STAGES" \
                                "$DEPENDENCY_ARG") # Pass the dependency argument

                            # Clean up the captured ID (remove any leading/trailing whitespace and ensure it's the last line)
                            NEW_SLURM_ID=$(echo "$NEW_SLURM_ID" | tail -n 1 | tr -d '[:space:]')

                            if [ -n "$NEW_SLURM_ID" ]; then
                                LAST_SLURM_ID="$NEW_SLURM_ID" # Update the last ID for the next iteration
                                echo "Submitted job with ID: $NEW_SLURM_ID. Dependency for next run: $LAST_SLURM_ID" # Added for better progress tracking
                            else
                                # If orchestrator.sh failed or didn't return an ID, reset LAST_SLURM_ID
                                # This prevents subsequent runs from depending on a non-existent job.
                                LAST_SLURM_ID=""
                                echo "Warning: orchestrator_single_experiment.sh for MODEL=$MODEL, QTYPE=$QTYPE, DTYPES=$DTYPES failed or returned no Job ID. Subsequent runs will not have a dependency from this one." >&2 # Log to stderr
                            fi
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