#!/bin/bash
# orchestrator_1.sh

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
# Worker script path (relative to where orchestrator_1.sh is run)
WORKER_SCRIPT="./scripts/run_experiment.sh"

# Parameters for the experiment
MODEL="Llama-3.1-8B-Instruct"
QTYPE="gsm"
DTYPES="clean"
SUBSET_NUM=100
TEMPERATURE=1
TOP_P=1
VLLM_MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"

OUTPUT_FOLDER="./$LOG_DIR/$DTYPES/$MODEL/$QTYPE"
mkdir -p "$OUTPUT_FOLDER"
OUTPUT_FILE="$OUTPUT_FOLDER/log_%j.txt" # This will be the output file for each submitted job

# ------------------------------------------------------------
log_message "Starting pipeline orchestration script."
log_message "Orchestration log file created at: $LOG_FILE"
log_message "Worker script to be used: $WORKER_SCRIPT"
log_message "Model: $MODEL, VLLM Model Name: $VLLM_MODEL_NAME, QType: $QTYPE" # Changed "Prefix" to "VLLM Model Name" for clarity
log_message "SLURM job outputs will be written to: $OUTPUT_FOLDER/log_JOBID.txt" # Clarified output path in log
log_message "============================================================="

# --- Stage 1: [0:2] ---
log_message "Submitting Stage 1 [0:2]..."
# Pass all 9 arguments: PART_START, PART_END, MODEL, QTYPE, DTYPES, SUBSET_NUM, TEMPERATURE, TOP_P, VLLM_MODEL_NAME
JOB_ID_S1=$(sbatch --parsable --output="$OUTPUT_FILE" "$WORKER_SCRIPT" 0 2 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 1 submitted. Job ID: $JOB_ID_S1"

# --- Stage 2: [2:4] ---
log_message "Submitting Stage 2 [2:4], dependent on Job ID: $JOB_ID_S1"
JOB_ID_S2=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S1 "$WORKER_SCRIPT" 2 4 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 2 submitted. Job ID: $JOB_ID_S2"

# --- Stage 3: [4:6] ---
log_message "Submitting Stage 3 [4:6], dependent on Job ID: $JOB_ID_S2"
JOB_ID_S3=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S2 "$WORKER_SCRIPT" 4 6 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 3 submitted. Job ID: $JOB_ID_S3"

# --- Stage 4: [6:8] ---
log_message "Submitting Stage 4 [6:8], dependent on Job ID: $JOB_ID_S3"
JOB_ID_S4=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S3 "$WORKER_SCRIPT" 6 8 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 4 submitted. Job ID: $JOB_ID_S4"

# --- Stage 5: [8:10] ---
log_message "Submitting Stage 5 [8:10], dependent on Job ID: $JOB_ID_S4"
JOB_ID_S5=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S4 "$WORKER_SCRIPT" 8 10 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 5 submitted. Job ID: $JOB_ID_S5" # Corrected log variable

# --- Stage 6: [10:12] ---
log_message "Submitting Stage 6 [10:12], dependent on Job ID: $JOB_ID_S5"
JOB_ID_S6=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S5 "$WORKER_SCRIPT" 10 12 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 6 submitted. Job ID: $JOB_ID_S6" # Corrected log variable

# --- Stage 7: [12:14] ---
log_message "Submitting Stage 7 [12:14], dependent on Job ID: $JOB_ID_S6" # Corrected dependency
JOB_ID_S7=$(sbatch --parsable --output="$OUTPUT_FILE" --dependency=afterok:$JOB_ID_S6 "$WORKER_SCRIPT" 12 14 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 7 submitted. Job ID: $JOB_ID_S7" # Corrected log variable

log_message "============================================================="
log_message "Pipeline orchestration complete. All stages submitted to SLURM."