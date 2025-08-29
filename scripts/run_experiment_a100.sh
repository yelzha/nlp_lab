#!/bin/bash
#SBATCH --partition=A100short
#SBATCH --time=07:59:59
#SBATCH --gpus=1
#SBATCH --ntasks=1
# cd ../

# --- Your actual job commands start here ---
echo "------------------------------------------------------------"
echo "SLURM JOB INFO"
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Partition: $SLURM_JOB_PARTITION"
echo "Nodes: $SLURM_NNODES"
echo "Tasks per node: $SLURM_NTASKS_PER_NODE"
echo "CPUs per task: $SLURM_CPUS_PER_TASK"
echo "Requested Memory: $SLURM_MEM_PER_NODE MB (approx)"
echo "Working Directory: $(pwd)"
echo "Start Time: $(date)"
echo "------------------------------------------------------------"

echo "Hello from Slurm on node $(hostname)!"

# ----------------- ENVIRONMENT SETUP ------------------

# ... (Environment setup commands omitted for brevity, assumed to be correct) ...

mkdir -p /home/s06zyelt/.my_tmp /home/s06zyelt/.cache/{huggingface,triton,nv}
export TMPDIR=/home/s06zyelt/.my_tmp
export TMP=$TMPDIR; export TEMP=$TMPDIR
export XDG_CACHE_HOME=/home/s06zyelt/.my_tmp/cache
export TRITON_CACHE_DIR=/home/s06zyelt/.cache/triton
export CUDA_CACHE_PATH=/home/s06zyelt/.cache/nv

# Hugging Face auth + caches
export HF_HOME=/home/s06zyelt/.cache/huggingface
export HUGGINGFACE_HUB_CACHE="$HF_HOME"
export TRANSFORMERS_CACHE="$HF_HOME/hub"

# python

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
module load CUDA/12.1.1

#source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
#conda activate /home/s06zyelt/nlp_lab/env
source /home/s06zyelt/nlp_lab/env/bin/activate

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
DEBUG=${10}
export DEBUG=${10}
EXPERIMENT_DIRECTORY=${11} # "experiments"
export MAIN_DIRECTORY=$(pwd)
export CUDA_LAUNCH_BLOCKING=1

# ----------------- MAIN LOOP ------------------

cd AgentForestRefactored/script

echo "============================================================="
echo "Running with agents on $QTYPE using $MODEL for $DTYPES"
echo "Processing parts from $PART_START to $PART_END"
echo "============================================================="

# Ensure DTYPES is passed correctly if the Python script expects a space-separated list
# Here we are assuming DTYPES is a single string like "clean"
sh run_reasoning_task.sh "$MODEL" "$QTYPE" "$DTYPES" "$PART_START" "$PART_END" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P" "$EXPERIMENT_DIRECTORY"

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "End Time: $(date)"
echo "Finished!!!"