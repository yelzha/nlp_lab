#!/bin/bash
# orchestrator.sh

# --- Logging Setup ---

# Define log directory and create it if it doesn't exist
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Generate a unique timestamp for the log file name
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="./$LOG_DIR/orchestrator_$TIMESTAMP.log"

# Function to log messages to both the console and the log file
log_message() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
}

# ----------------------------------------------------

# --- Define the worker script filename and fixed parameters ---
# Worker script path (relative to where orchestrator.sh is run)
WORKER_SCRIPT="./scripts/run_experiment.sh"

# Parameters for the experiment
MODEL="gemma-3-4b-it"
QTYPE="gsm"
DTYPES="clean"
SUBSET_NUM=100
TEMPERATURE=1
TOP_P=1
VLLM_MODEL_NAME="google/gemma-3-4b-it"

OUTPUT_FOLDER="./$LOG_DIR/$DTYPES/$MODEL/$QTYPE"
mkdir -p "$OUTPUT_FOLDER"
OUTPUT_FILE="$OUTPUT_FOLDER/log_%j.txt"

# ------------------------------------------------------------
log_message "Starting pipeline orchestration script."
log_message "Orchestration log file created at: $LOG_FILE"
log_message "Worker script to be used: $WORKER_SCRIPT"
log_message "Model: $MODEL, Prefix: $VLLM_MODEL_NAME, QType: $QTYPE"
log_message "============================================================="

# --- Stage 1: [0:3] ---
log_message "Submitting Stage 1 [0:3]..."
# Pass all 9 arguments: PART_START, PART_END, MODEL, QTYPE, DTYPES, SUBSET_NUM, TEMPERATURE, TOP_P, VLLM_MODEL_NAME
JOB_ID_S1=$(sbatch --parsable --output="$OUTPUT_FILE" "$WORKER_SCRIPT" 0 3 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 1 submitted. Job ID: $JOB_ID_S1"

# --- Stage 2: [3:6] ---
log_message "Submitting Stage 2 [3:6], dependent on Job ID: $JOB_ID_S1"
# Stage 2 depends on Stage 1
JOB_ID_S2=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S1 "$WORKER_SCRIPT" 3 6 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 2 submitted. Job ID: $JOB_ID_S2"

# --- Stage 3: [6:9] ---
log_message "Submitting Stage 3 [6:9], dependent on Job ID: $JOB_ID_S2"
# Stage 3 depends on Stage 2
JOB_ID_S3=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S2 "$WORKER_SCRIPT" 6 9 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 3 submitted. Job ID: $JOB_ID_S3"

# --- Stage 4: [9:12] ---
log_message "Submitting Stage 4 [9:12], dependent on Job ID: $JOB_ID_S3"
# Stage 4 depends on Stage 3
JOB_ID_S4=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S3 "$WORKER_SCRIPT" 9 12 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 4 submitted. Job ID: $JOB_ID_S4"

# --- Stage 5: [12:14] ---
log_message "Submitting Stage 5 [12:14], dependent on Job ID: $JOB_ID_S4"
# Stage 5 depends on Stage 4
JOB_ID_S5=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S4 "$WORKER_SCRIPT" 12 14 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 5 submitted. Job ID: $JOB_ID_S5"

log_message "============================================================="
log_message "Pipeline orchestration complete. All stages submitted to SLURM."