#!/bin/bash
# orchestrator.sh

# --- Logging Setup ---

# Define log directory and create it if it doesn't exist
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# Generate a unique timestamp for the log file name
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/orchestrator_$TIMESTAMP.log"

# Function to log messages to both the console and the log file
log_message() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
}

# ----------------------------------------------------

# --- Define the worker script filename as a constant parameter ---
# Make sure the path is correct relative to where orchestrator.sh is run
WORKER_SCRIPT="./scripts/run_clean_gemma-3-4b-it_1-50.sh"

log_message "Starting pipeline orchestration script for 5 chunks (1500 parts total)."
log_message "Orchestration log file created at: $LOG_FILE"
log_message "Worker script to be used: $WORKER_SCRIPT"
log_message "============================================================="

# --- Stage 1: [0:299] ---
log_message "Submitting Stage 1 [0:299]..."
# Use the WORKER_SCRIPT variable
JOB_ID_S1=$(sbatch --parsable "$WORKER_SCRIPT" 0 3)
log_message "Stage 1 submitted. Job ID: $JOB_ID_S1"

# --- Stage 2: [300:599] ---
log_message "Submitting Stage 2 [300:599], dependent on Job ID: $JOB_ID_S1"
# Use the WORKER_SCRIPT variable
JOB_ID_S2=$(sbatch --parsable --dependency=afterok:$JOB_ID_S1 "$WORKER_SCRIPT" 3 6)
log_message "Stage 2 submitted. Job ID: $JOB_ID_S2"

# --- Stage 3: [600:899] ---
log_message "Submitting Stage 3 [600:899], dependent on Job ID: $JOB_ID_S2"
# Use the WORKER_SCRIPT variable
JOB_ID_S3=$(sbatch --parsable --dependency=afterok:$JOB_ID_S2 "$WORKER_SCRIPT" 6 9)
log_message "Stage 3 submitted. Job ID: $JOB_ID_S3"

# --- Stage 4: [900:1199] ---
log_message "Submitting Stage 4 [900:1199], dependent on Job ID: $JOB_ID_S3"
# Use the WORKER_SCRIPT variable
JOB_ID_S4=$(sbatch --parsable --dependency=afterok:$JOB_ID_S3 "$WORKER_SCRIPT" 9 12)
log_message "Stage 4 submitted. Job ID: $JOB_ID_S4"

# --- Stage 5: [1200:1499] ---
log_message "Submitting Stage 5 [1200:1499], dependent on Job ID: $JOB_ID_S4"
# Use the WORKER_SCRIPT variable
JOB_ID_S5=$(sbatch --parsable --dependency=afterok:$JOB_ID_S4 "$WORKER_SCRIPT" 12 14)
log_message "Stage 5 submitted. Job ID: $JOB_ID_S5"

log_message "============================================================="
log_message "Pipeline orchestration complete. All stages submitted to SLURM."