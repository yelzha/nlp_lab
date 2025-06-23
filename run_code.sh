#!/bin/bash
#SBATCH --partition=A100devel
#SBATCH --time=0:20:00
#SBATCH --gpus=1
#SBATCH --ntasks=1
#SBATCH --output=slurm_output.txt   # Log everything here

#cd $SLURM_SUBMIT_DIR
export OLLAMA_HOST=127.0.0.1:11500

ollama serve &
sleep 5

ollama run qwen3:0.6b || true

module load Python/3.11.3-GCCcore-12.3.0
source venv/bin/activate

# Force CPU-safe installs
# pip install --no-binary :all: numpy pandas sacrebleu openai
# pip install --no-binary :all: wheel setuptools
# pip install git+https://github.com/openai/human-eval.git

cd AgentForest/script
sh run_experiments.sh
# python ollama_test.py

pkill ollama
