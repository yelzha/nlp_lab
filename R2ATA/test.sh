#!/bin/bash


nvidia-smi
python -c "import torch,os; print('cuda_avail=', torch.cuda.is_available(), 'num=', torch.cuda.device_count(), 'vis=', os.environ.get('CUDA_VISIBLE_DEVICES'))"