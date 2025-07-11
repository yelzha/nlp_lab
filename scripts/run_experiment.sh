#!/bin/bash
#SBATCH --partition=A100short
#SBATCH --time=07:59:59
#SBATCH --gpus=1
#SBATCH --ntasks=1
# #SBATCH --output=../logs/clean_gemma-3-12b-it_%j.txt
# cd ../

# --- Your actual job commands start here ---
echo "------------------------------------------------------------"
echo "SLURM JOB INFO"
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
# ... (SLURM info continued) ...
echo "Working Directory: $(pwd)"
echo "Start Time: $(date)"
echo "------------------------------------------------------------"

echo "Hello from Slurm on node $(hostname)!"

# ----------------- ENVIRONMENT SETUP ------------------

# ... (Environment setup commands omitted for brevity, assumed to be correct) ...

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
module load CUDA/12.1.1

source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

pip install numpy pandas
pip install sacrebleu
pip install git+https://github.com/openai/human-eval.git

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121

python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'PyTorch CUDA version: {torch.version.cuda}')"
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"


echo "Running AgentForest experiments..."

# ----------------- EXPERIMENT CONFIG (Accepting Input Arguments) ------------------

# Check if the required number of arguments are provided
if [ "$#" -lt 9 ]; then
    echo "Error: Missing input arguments."
    echo "Usage: $0 PART_START PART_END MODEL QTYPE DTYPES SUBSET_NUM TEMPERATURE TOP_P VLLM_MODEL_NAME"
    exit 1
fi

# Assign input arguments to variables
PART_START=$1
PART_END=$2
MODEL=$3
QTYPE=$4
DTYPES=$5
SUBSET_NUM=$6
TEMPERATURE=$7
TOP_P=$8
VLLM_MODEL_NAME=$9
export VLLM_MODEL_NAME=$9

# ----------------- MAIN LOOP ------------------

cd AgentForestRefactored/script

echo "============================================================="
echo "Running with agents on $QTYPE using $MODEL for $DTYPES"
echo "Processing parts from $PART_START to $PART_END"
echo "============================================================="

# Ensure DTYPES is passed correctly if the Python script expects a space-separated list
# Here we are assuming DTYPES is a single string like "clean"
sh run_reasoning_task.sh "$MODEL" "$QTYPE" "$DTYPES" "$PART_START" "$PART_END" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P"

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "End Time: $(date)"
echo "Finished!!!"