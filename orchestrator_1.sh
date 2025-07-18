#!/bin/bash
# orchestrator_loop.sh

# --- Logging Setup ---

# Define log directory and create it if it doesn't exist
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Generate a unique timestamp for the log file name
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="./$LOG_DIR/orchestrator/orchestrator_$TIMESTAMP.log"

# Function to log messages to both the console and the log file
log_message() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
}

# ----------------------------------------------------

# --- Define the worker script filename and fixed parameters ---
# Worker script path (relative to where orchestrator_loop.sh is run)
WORKER_SCRIPT="./scripts/run_experiment_a100.sh"

# Parameters for the experiment
MODEL="Qwen3-4b"
QTYPE="mmlu"
DTYPES="clean"
SUBSET_NUM=100
TEMPERATURE=1
TOP_P=1
VLLM_MODEL_NAME="Qwen/Qwen3-4b" # Full VLLM model name
DEBUG="False"

# Define the base output folder for logs (relative to orchestrator.sh)
OUTPUT_BASE_FOLDER="./$LOG_DIR/$DTYPES/$MODEL/$QTYPE"
mkdir -p "$OUTPUT_BASE_FOLDER" # Ensure the base folder exists

# ------------------------------------------------------------
log_message "Starting pipeline orchestration script."
log_message "### DEBUG is: $DEBUG ###"
log_message "Orchestration log file created at: $LOG_FILE"
log_message "Worker script to be used: $WORKER_SCRIPT"
log_message "Model: $MODEL, VLLM Model Name: $VLLM_MODEL_NAME, QType: $QTYPE"
log_message "SLURM job outputs will be written to: $OUTPUT_BASE_FOLDER/run_JOBNAME_JOBID.txt" # Clarified output path in log
log_message "============================================================="

# --- Define the stages (start and end values) ---
# Each pair represents [start_index, end_index] for the worker script
STAGES=(
    "0 2"
    "2 4"
    "4 6"
    "6 8"
    "8 10"
)

# Initialize the job ID for dependency. The first job has no dependency.
PREV_JOB_ID=""

# --- Loop through stages and submit jobs ---
for i in "${!STAGES[@]}"; do
    # Extract start and end from the current stage string
    read -r START_INDEX END_INDEX <<< "${STAGES[$i]}"

    # Calculate stage number (0-indexed array, so add 1 for user-friendly numbering)
    STAGE_NUM=$((i + 1))

    log_message "Submitting Stage $STAGE_NUM [$START_INDEX:$END_INDEX]..."

    JOB_NAME="run_${MODEL}_${QTYPE}_${DTYPES}_stage${STAGE_NUM}"
    OUTPUT_FILE="$OUTPUT_BASE_FOLDER/${JOB_NAME}_%j.txt"

    # Build the sbatch command
    SBATCH_CMD="sbatch --parsable --job-name=\"$JOB_NAME\" --output=\"$OUTPUT_FILE\""

    # Add dependency if it's not the first job
    if [ -n "$PREV_JOB_ID" ]; then
        SBATCH_CMD+=" --dependency=afterok:$PREV_JOB_ID"
        log_message "  Dependent on Job ID: $PREV_JOB_ID"
    fi

    # Append worker script and its arguments
    SBATCH_CMD+=" \"$WORKER_SCRIPT\" $START_INDEX $END_INDEX \"$MODEL\" \"$QTYPE\" \"$DTYPES\" \"$SUBSET_NUM\" \"$TEMPERATURE\" \"$TOP_P\" \"$VLLM_MODEL_NAME\" \"$DEBUG\""

    # Execute the sbatch command
    CURRENT_JOB_ID=$(eval "$SBATCH_CMD") # Use eval to execute the constructed command string
    CURRENT_JOB_ID=$(echo "$CURRENT_JOB_ID" | tr -d '[:space:]') # Remove any whitespace

    log_message "Stage $STAGE_NUM submitted. Job ID: $CURRENT_JOB_ID. Job Name: $JOB_NAME. Output: $OUTPUT_FILE"

    # Update PREV_JOB_ID for the next iteration's dependency
    PREV_JOB_ID="$CURRENT_JOB_ID"
done

log_message "============================================================="
log_message "Pipeline orchestration complete. All stages submitted to SLURM."
