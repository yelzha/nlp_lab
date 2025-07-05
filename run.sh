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
pip install sacrebleu
pip install git+https://github.com/openai/human-eval.git

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121


echo "Running AgentForest experiments..."
cd AgentForest/script


MODEL="qwen3:4b" # qwen3:0.6b
# mistral:7b-instruct-v0.3 llama3:8b-instruct
# gemma:4b gemma:12b
# qwen3:4b qwen3:14b
export VLLM_MODEL_NAME="Qwen/Qwen3-4B"

QTYPE="gsm" # mmlu, math, chess, human-eval, gsm

AGENT_COUNTS=(1 5) # (1 5 10 15 20 25 30 35 40 45 50)
DTYPES=("clean") # clean, aeda, typo

# Loop through each agent count and run the main script
for AGENT in "${AGENT_COUNTS[@]}"
do
    echo "============================================================="
    echo "Running with $AGENT agents on $QTYPE using $MODEL for $DTYPES"
    echo "============================================================="

    sh run_reasoning_task.sh "$AGENT" 1 100 "$MODEL" "$QTYPE" "$DTYPES"

    echo "============================================================="
    echo "========================+Finished+==========================="
    echo "============================================================="
done

echo "Terminating vLLM server..."
kill $VLLM_PID

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"
