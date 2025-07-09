#!/bin/bash
#SBATCH --partition=A100medium
#SBATCH --time=23:59:59
#SBATCH --gpus=1
#SBATCH --ntasks=2
#SBATCH --output=slurm_output_vllm_%j.txt

# ----------------- ENVIRONMENT SETUP ------------------

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
#module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1
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

# ----------------- EXPERIMENT CONFIG ------------------

MODEL="qwen3:4b"
export VLLM_MODEL_NAME="Qwen/Qwen3-4B"

QTYPE="gsm" # mmlu, math, chess, human-eval, gsm
DTYPES=("clean") # clean, aeda, typo

PART_START=0
PART_END=13
SUBSET_NUM=100

TEMPERATURE=1 # 0.3 0.7
TOP_P=1 # 0.95,0.9

cd AgentForestRefactored/script

# ----------------- MAIN LOOP ------------------

echo "============================================================="
echo "Running with agents on $QTYPE using $MODEL for $DTYPES"
echo "============================================================="

sh run_reasoning_task.sh "$MODEL" "$QTYPE" "$DTYPES" "$PART_START" "$PART_END" "$SUBSET_NUM" "$TEMPERATURE" "$TOP_P"

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"
