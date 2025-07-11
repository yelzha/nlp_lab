#!/bin/bash
#SBATCH --partition=A40medium
#SBATCH --time=23:59:00
#SBATCH --gpus=4
#SBATCH --ntasks=8
#SBATCH --output=../logs/slurm_output_ollama_%j.txt
cd ../

#cd $SLURM_SUBMIT_DIR
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_HOST=127.0.0.1:11500
export LLM_IP="localhost:11500"

ollama serve &
sleep 5

ollama run qwen3:4b || true # qwen3:0.6b
# mistral:7b-instruct-v0.3 llama3:8b-instruct
# gemma:4b gemma:12b
# qwen3:4b qwen3:14b

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs

#conda create -p /home/s06zyelt/nlp_lab/env python=3.10 -y
source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

pip install numpy pandas
pip install openai==0.28.1
pip install sacrebleu
pip install git+https://github.com/openai/human-eval.git

cd AgentForest/script
sh run_experiments.sh
# python ollama_test.py

pkill ollama

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
