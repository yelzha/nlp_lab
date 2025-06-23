#!/bin/bash
#SBATCH --partition=A40devel
#SBATCH --time=0:05:00
#SBATCH --gpus=1
#SBATCH --ntasks=1
#SBATCH --output=slurm_output.txt   # Log everything here

#cd $SLURM_SUBMIT_DIR
export OLLAMA_HOST=127.0.0.1:11500

ollama serve &
sleep 5

ollama run qwen3:14b || true

module load Python/3.11.3-GCCcore-12.3.0
source venv/bin/activate
python ollama_test.py

pkill ollama
