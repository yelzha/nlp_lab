#!/bin/bash
#SBATCH --partition=A100medium
#SBATCH --time=23:59:00
#SBATCH --gpus=1
#SBATCH --ntasks=4
#SBATCH --output=slurm_output_vllm_%j.txt


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
cd AgentForest/script
sh run_experiments.sh

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Finished!!!"
