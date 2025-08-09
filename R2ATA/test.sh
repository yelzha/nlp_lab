#!/bin/bash
#SBATCH --partition=A40short
#SBATCH --time=07:59:59
#SBATCH --gpus=1
#SBATCH --ntasks=1

nvidia-smi
python -c "import torch,os; print('cuda_avail=', torch.cuda.is_available(), 'num=', torch.cuda.device_count(), 'vis=', os.environ.get('CUDA_VISIBLE_DEVICES'))"