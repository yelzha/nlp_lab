#!/bin/bash
# orchestrator_single_experiment.sh
# This script orchestrates SLURM job submissions based on direct command-line parameters.
# It now accepts an optional initial dependency job ID and outputs the last submitted job ID.

# --- Logging Setup ---
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="" # Will be set after parameters are known

log_message() {
    # Send message to stderr (visible in terminal, but not captured by calling script)
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" >&2
    # Also write to the log file
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" >> "$LOG_FILE"
}

# --- Parameter Parsing ---
# Expected arguments:
# 1: MODEL
# 2: QTYPE
# 3: DTYPES
# 4: SUBSET_NUM
# 5: TEMPERATURE
# 6: TOP_P
# 7: VLLM_MODEL_NAME
# 8: DEBUG
# 9: STAGES_STRING (e.g., "0 2;2 4;4 6")
# 10: INITIAL_DEPENDENCY_JOB_ID (optional)

MODEL="$1"
QTYPE="$2"
DTYPES="$3"
SUBSET_NUM="$4"
TEMPERATURE="$5"
TOP_P="$6"
VLLM_MODEL_NAME="$7"
DEBUG="$8"
STAGES_STRING="$9"
INITIAL_DEPENDENCY_JOB_ID="${10}"

# Validate essential parameters
if [ -z "$MODEL" ] || [ -z "$QTYPE" ] || [ -z "$DTYPES" ] || [ -z "$STAGES_STRING" ]; then
    echo "Usage: $0 <MODEL> <QTYPE> <DTYPES> <SUBSET_NUM> <TEMPERATURE> <TOP_P> <VLLM_MODEL_NAME> <DEBUG> \"<STAGES_STRING>\" [initial_dependency_job_id]" >&2 # Send usage to stderr
    exit 1
fi

# Set the log file based on the parameters
PARAMS_HASH=$(echo "${MODEL}_${QTYPE}_${DTYPES}_${SUBSET_NUM}_${TEMPERATURE}_${TOP_P}_${VLLM_MODEL_NAME}_${DEBUG}" | md5sum | cut -d ' ' -f 1)
LOG_FILE="./$LOG_DIR/orchestrator/${PARAMS_HASH}_orchestrator_$TIMESTAMP.log"
mkdir -p "$(dirname "$LOG_FILE")" # Ensure orchestrator log directory exists

log_message "Starting orchestrator_single_experiment.sh with parameters:"
log_message "  MODEL: $MODEL"
log_message "  QTYPE: $QTYPE"
log_message "  DTYPES: $DTYPES"
log_message "  SUBSET_NUM: $SUBSET_NUM"
log_message "  TEMPERATURE: $TEMPERATURE"
log_message "  TOP_P: $TOP_P"
log_message "  VLLM_MODEL_NAME: $VLLM_MODEL_NAME"
log_message "  DEBUG: $DEBUG"
log_message "  STAGES_STRING: \"$STAGES_STRING\""
if [ -n "$INITIAL_DEPENDENCY_JOB_ID" ]; then
    log_message "  Initial external dependency set to: $INITIAL_DEPENDENCY_JOB_ID"
fi
log_message "Orchestration log file created at: $LOG_FILE"

# Parse STAGES_STRING into an array
IFS=';' read -r -a STAGES <<< "$STAGES_STRING"
if [ ${#STAGES[@]} -eq 0 ]; then
    log_message "Error: No STAGES defined in STAGES_STRING: $STAGES_STRING."
    exit 1
fi

# --- Define the worker script filename ---
WORKER_SCRIPT="./scripts/run_experiment_a100.sh"

# Define the base output folder for SLURM job logs
OUTPUT_BASE_FOLDER="./$LOG_DIR/$DTYPES/$MODEL/$QTYPE"
mkdir -p "$OUTPUT_BASE_FOLDER" # Ensure the base folder exists

log_message "Worker script to be used: $WORKER_SCRIPT"
log_message "SLURM job outputs will be written to: $OUTPUT_BASE_FOLDER/run_JOBNAME_JOBID.txt"
log_message "============================================================="

# Initialize the job ID for dependency.
PREV_JOB_ID="$INITIAL_DEPENDENCY_JOB_ID"

# --- Loop through stages and submit jobs ---
for i in "${!STAGES[@]}"; do
    read -r START_INDEX END_INDEX <<< "${STAGES[$i]}"
    STAGE_NUM=$((i + 1)) # Stage number (1-indexed)

    log_message "Submitting Stage $STAGE_NUM [$START_INDEX:$END_INDEX]..."

    JOB_NAME="run_${MODEL}_${QTYPE}_${DTYPES}_stage${STAGE_NUM}"
    OUTPUT_FILE="$OUTPUT_BASE_FOLDER/${JOB_NAME}_%j.txt"

    SBATCH_CMD="sbatch --parsable --job-name=\"$JOB_NAME\" --output=\"$OUTPUT_FILE\""
    if [ -n "$PREV_JOB_ID" ]; then
        SBATCH_CMD+=" --dependency=afterok:$PREV_JOB_ID"
        log_message "  Dependent on Job ID: $PREV_JOB_ID"
    fi

    SBATCH_CMD+=" \"$WORKER_SCRIPT\" \"$START_INDEX\" \"$END_INDEX\" \"$MODEL\" \"$QTYPE\" \"$DTYPES\" \"$SUBSET_NUM\" \"$TEMPERATURE\" \"$TOP_P\" \"$VLLM_MODEL_NAME\" \"$DEBUG\""



    # Execute sbatch directly from the array. This avoids the 'eval' problem.
    CURRENT_JOB_ID=$(eval "$SBATCH_CMD")
    CURRENT_JOB_ID=$(echo "$CURRENT_JOB_ID" | tr -d '[:space:]') # Remove any whitespace

    if [ -z "$CURRENT_JOB_ID" ]; then
        log_message "Error: sbatch command failed to return a Job ID for Stage $STAGE_NUM."
        log_message "Command attempted: sbatch ${SBATCH_CMD}" # Log the exact command
        exit 1 # Exit if a job submission fails
    fi

    log_message "Stage $STAGE_NUM submitted. Job ID: $CURRENT_JOB_ID. Job Name: $JOB_NAME. Output: $OUTPUT_FILE"

    # Update PREV_JOB_ID for the next iteration
    PREV_JOB_ID="$CURRENT_JOB_ID"
done

log_message "============================================================="
log_message "Pipeline orchestration complete. All stages submitted to SLURM."

# Output the last submitted job ID to stdout for the calling script to capture
# This must be the ONLY thing printed to stdout by this script.
echo "$PREV_JOB_ID"