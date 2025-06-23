#!/bin/bash
#SBATCH --partition=A100devel
#SBATCH --time=0:20:00
#SBATCH --gpus=1
#SBATCH --output=slurm_output.txt   # Log everything here


module load Python/3.11.3-GCCcore-12.3.0
source venv/bin/activate

python -c "import numpy, pandas, openai; print('All good')"
