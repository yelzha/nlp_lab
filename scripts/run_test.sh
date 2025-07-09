#!/bin/bash
#SBATCH --partition=A100devel
#SBATCH --time=0:59:00
#SBATCH --gpus=1
#SBATCH --ntasks=4
#SBATCH --output=../logs/slurm_output_test.txt   # Log everything here
cd ../

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
module load CUDA/12.1.1

source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'PyTorch CUDA version: {torch.version.cuda}')"
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"

echo "Running Test experiments..."
python vllm_test.py

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"

# Note: The vLLM server command will run until the job time limit is reached or it's manually stopped.
# For actual usage, you might want to run this in a separate, longer-running job or a persistent service.
