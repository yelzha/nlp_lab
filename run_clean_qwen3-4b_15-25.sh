#!/bin/bash
#SBATCH --partition=A100medium
#SBATCH --time=23:59:00
#SBATCH --gpus=4
#SBATCH --ntasks=4
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
AGENT_COUNTS=(15 20 25)
DTYPES=("clean") # clean, aeda, typo

cd AgentForest/script

# ----------------- MAIN LOOP ------------------

for AGENT in "${AGENT_COUNTS[@]}"
do
    echo "============================================================="
    echo "Running with $AGENT agents on $QTYPE using $MODEL for $DTYPES"
    echo "============================================================="

    sh run_reasoning_task.sh "$AGENT" 14 100 "$MODEL" "$QTYPE" "$DTYPES"

    echo "============================================================="
    echo "========================+Finished+==========================="
    echo "============================================================="
done

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"
