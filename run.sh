#!/bin/bash
#SBATCH --partition=A40medium
#SBATCH --time=23:59:00
#SBATCH --gpus=4
#SBATCH --ntasks=8
#SBATCH --output=slurm_output_vllm_%j.txt

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs

module load CUDA/12.1.1
module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1

source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

pip install numpy pandas
pip install openai==0.28.1
pip install sacrebleu
pip install git+https://github.com/openai/human-eval.git

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121

export LLM_IP="localhost:11500"

echo "Attempting to start vLLM server..."

vllm serve Qwen/Qwen3-4B \
    --model Qwen/Qwen3-4B \
    --host 127.0.0.1 \
    --port 11500 \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 512 \
    --dtype auto \
    --disable-log-requests &

VLLM_PID=$!

sleep 15

python -c "import numpy, pandas, openai, torch, vllm; print('All good')"
python -c "from human_eval.data import read_problems; print('human_eval works')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'PyTorch CUDA version: {torch.version.cuda}')"
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"

echo "Running AgentForest experiments..."
cd AgentForest/script
sh run_experiments.sh

echo "Terminating vLLM server..."
kill $VLLM_PID

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"
