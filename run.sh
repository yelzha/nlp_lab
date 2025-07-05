#!/bin/bash
#SBATCH --partition=A100devel
#SBATCH --time=0:59:00
#SBATCH --gpus=1
#SBATCH --ntasks=1
#SBATCH --output=slurm_output_vllm_%j.txt

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs

module load CUDA/12.1.1
module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1

source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

pip install numpy pandas
pip install sacrebleu
pip install git+https://github.com/openai/human-eval.git

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121


echo "Running AgentForest experiments..."
cd AgentForest/script
sh run_experiments.sh

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"
