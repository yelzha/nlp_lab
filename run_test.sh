#!/bin/bash
#SBATCH --partition=A100devel
#SBATCH --time=0:20:00
#SBATCH --gpus=1
#SBATCH --output=slurm_output.txt   # Log everything here


module load Python/3.11.3-GCCcore-12.3.0
module load Miniforge3

conda create -n nlp_env python=3.11 numpy pandas -y
conda activate /home/s06zyelt/nlp_lab/env

#pip install openai sacrebleu
#pip install git+https://github.com/openai/human-eval.git

python -c "import numpy, pandas, openai; print('All good')"
