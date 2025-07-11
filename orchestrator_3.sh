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
TOP_P=0.95
VLLM_MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct" # Full VLLM model name

# Define the base output folder for logs (relative to orchestrator.sh)
OUTPUT_BASE_FOLDER="./$LOG_DIR/$DTYPES/$MODEL/$QTYPE"
mkdir -p "$OUTPUT_BASE_FOLDER" # Ensure the base folder exists

# ------------------------------------------------------------
log_message "Starting pipeline orchestration script."
log_message "Orchestration log file created at: $LOG_FILE"
log_message "Worker script to be used: $WORKER_SCRIPT"
log_message "Model: $MODEL, VLLM Model Name: $VLLM_MODEL_NAME, QType: $QTYPE"
log_message "SLURM job outputs will be written to: $OUTPUT_BASE_FOLDER/run_JOBNAME_JOBID.txt" # Clarified output path in log
log_message "============================================================="

# --- Stage 1: [0:2] ---
log_message "Submitting Stage 1 [0:2]..."
JOB_NAME_S1="run_${MODEL}_${QTYPE}_${DTYPES}_stage1"
# Use --job-name to set the job name, and include %x (job name) in the output file
OUTPUT_FILE_S1="$OUTPUT_BASE_FOLDER/${JOB_NAME_S1}_%j.txt"
JOB_ID_S1=$(sbatch --parsable --job-name="$JOB_NAME_S1" --output="$OUTPUT_FILE_S1" "$WORKER_SCRIPT" 0 2 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 1 submitted. Job ID: $JOB_ID_S1. Job Name: $JOB_NAME_S1. Output: $OUTPUT_FILE_S1"

# --- Stage 2: [2:4] ---
log_message "Submitting Stage 2 [2:4], dependent on Job ID: $JOB_ID_S1"
JOB_NAME_S2="run_${MODEL}_${QTYPE}_${DTYPES}_stage2"
OUTPUT_FILE_S2="$OUTPUT_BASE_FOLDER/${JOB_NAME_S2}_%j.txt"
JOB_ID_S2=$(sbatch --parsable --job-name="$JOB_NAME_S2" --output="$OUTPUT_FILE_S2" --dependency=afterok:$JOB_ID_S1 "$WORKER_SCRIPT" 2 4 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 2 submitted. Job ID: $JOB_ID_S2. Job Name: $JOB_NAME_S2. Output: $OUTPUT_FILE_S2"

# --- Stage 3: [4:6] ---
log_message "Submitting Stage 3 [4:6], dependent on Job ID: $JOB_ID_S2"
JOB_NAME_S3="run_${MODEL}_${QTYPE}_${DTYPES}_stage3"
OUTPUT_FILE_S3="$OUTPUT_BASE_FOLDER/${JOB_NAME_S3}_%j.txt"
JOB_ID_S3=$(sbatch --parsable --job-name="$JOB_NAME_S3" --output="$OUTPUT_FILE_S3" --dependency=afterok:$JOB_ID_S2 "$WORKER_SCRIPT" 4 6 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 3 submitted. Job ID: $JOB_ID_S3. Job Name: $JOB_NAME_S3. Output: $OUTPUT_FILE_S3"

# --- Stage 4: [6:8] ---
log_message "Submitting Stage 4 [6:8], dependent on Job ID: $JOB_ID_S3"
JOB_NAME_S4="run_${MODEL}_${QTYPE}_${DTYPES}_stage4"
OUTPUT_FILE_S4="$OUTPUT_BASE_FOLDER/${JOB_NAME_S4}_%j.txt"
JOB_ID_S4=$(sbatch --parsable --job-name="$JOB_NAME_S4" --output="$OUTPUT_FILE_S4" --dependency=afterok:$JOB_ID_S3 "$WORKER_SCRIPT" 6 8 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 4 submitted. Job ID: $JOB_ID_S4. Job Name: $JOB_NAME_S4. Output: $OUTPUT_FILE_S4"

# --- Stage 5: [8:10] ---
log_message "Submitting Stage 5 [8:10], dependent on Job ID: $JOB_ID_S4"
JOB_NAME_S5="run_${MODEL}_${QTYPE}_${DTYPES}_stage5"
OUTPUT_FILE_S5="$OUTPUT_BASE_FOLDER/${JOB_NAME_S5}_%j.txt"
JOB_ID_S5=$(sbatch --parsable --job-name="$JOB_NAME_S5" --output="$OUTPUT_FILE_S5" --dependency=afterok:$JOB_ID_S4 "$WORKER_SCRIPT" 8 10 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 5 submitted. Job ID: $JOB_ID_S5. Job Name: $JOB_NAME_S5. Output: $OUTPUT_FILE_S5"

# --- Stage 6: [10:12] ---
log_message "Submitting Stage 6 [10:12], dependent on Job ID: $JOB_ID_S5"
JOB_NAME_S6="run_${MODEL}_${QTYPE}_${DTYPES}_stage6"
OUTPUT_FILE_S6="$OUTPUT_BASE_FOLDER/${JOB_NAME_S6}_%j.txt"
JOB_ID_S6=$(sbatch --parsable --job-name="$JOB_NAME_S6" --output="$OUTPUT_FILE_S6" --dependency=afterok:$JOB_ID_S5 "$WORKER_SCRIPT" 10 12 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 6 submitted. Job ID: $JOB_ID_S6. Job Name: $JOB_NAME_S6. Output: $OUTPUT_FILE_S6"

# --- Stage 7: [12:14] ---
log_message "Submitting Stage 7 [12:14], dependent on Job ID: $JOB_ID_S6"
JOB_NAME_S7="run_${MODEL}_${QTYPE}_${DTYPES}_stage7"
OUTPUT_FILE_S7="$OUTPUT_BASE_FOLDER/${JOB_NAME_S7}_%j.txt"
JOB_ID_S7=$(sbatch --parsable --job-name="$JOB_NAME_S7" --output="$OUTPUT_FILE_S7" --dependency=afterok:$JOB_ID_S6 "$WORKER_SCRIPT" 12 14 "$MODEL" "$QTYPE" "$DTYPES" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$VLLM_MODEL_NAME")
log_message "Stage 7 submitted. Job ID: $JOB_ID_S7. Job Name: $JOB_NAME_S7. Output: $OUTPUT_FILE_S7"

log_message "============================================================="
log_message "Pipeline orchestration complete. All stages submitted to SLURM."