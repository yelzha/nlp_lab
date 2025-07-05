#!/bin/bash
#SBATCH --partition=A40devel
#SBATCH --time=0:59:00
#SBATCH --gpus=4
#SBATCH --output=slurm_output_test.txt   # Log everything here

# Load necessary modules first
# This ensures CUDA libraries are available in the environment
module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
#module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1
module load CUDA/12.1.1

# Activate your Conda environment
source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

# Install core Python packages
#pip install numpy pandas
#pip install openai==0.28.1
#pip install sacrebleu
#pip install git+https://github.com/openai/human-eval.git

# Install PyTorch and vLLM, ensuring they are compiled for CUDA 12.1
# This is crucial for vLLM to find and use your GPU
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify installations
#python -c "import numpy, pandas, openai, torch, vllm; print('All good')"
#python -c "from human_eval.data import read_problems; print('human_eval works')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'PyTorch CUDA version: {torch.version.cuda}')"

echo "Attempting to start vLLM server..."

# Start the vLLM server with optimized parameters for your A100 and GSM8K
# Removed --enforce-eager as it's generally not needed and can sometimes hinder CUDA graph optimizations
vllm serve Qwen/Qwen3-4B \
    --host 127.0.0.1 \
    --port 11500 \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 512 \
    --dtype auto \
    --disable-log-requests &

VLLM_PID=$!
sleep 300

echo "Finished to start vLLM server..."
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"

export LLM_IP="localhost:11500"
python vllm_test.py


echo "Terminating vLLM server..."
kill $VLLM_PID

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"

# Note: The vLLM server command will run until the job time limit is reached or it's manually stopped.
# For actual usage, you might want to run this in a separate, longer-running job or a persistent service.
