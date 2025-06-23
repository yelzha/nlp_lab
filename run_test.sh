#!/bin/bash
#SBATCH --partition=A100devel
#SBATCH --time=0:20:00
#SBATCH --gpus=1
#SBATCH --output=slurm_output.txt   # Log everything here

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs


#conda create -p /home/s06zyelt/nlp_lab/env python=3.10 -y
source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

#pip install numpy pandas
#pip install openai sacrebleu
#pip install git+https://github.com/openai/human-eval.git

python -c "import numpy, pandas, openai; print('All good')"

echo "Finished!!!"