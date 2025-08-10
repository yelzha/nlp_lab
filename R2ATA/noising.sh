#!/bin/bash
#SBATCH --partition=A40medium
#SBATCH --time=23:59:59
#SBATCH --gpus=1
#SBATCH --ntasks=1

export WANDB_MODE=disabled

# Optionally set the cache for transformers
# export TRANSFORMERS_CACHE='YOUR_PATH/huggingface'

# Read arguments
export model=$1                # 'mistral', 'gemma' or 'llama'
export test_set=$2              # 'gsm8k', 'mmlu'
export n_steps=$3              # number of edits
export batch_size=$4           # batch size
export few_shot=$5

#module load Miniforge3
#module load git/2.41.0-GCCcore-12.3.0-nodocs
#source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
#source venv/bin/activate

# Create results folder if it doesn't exist
results_dir="experiments/results"
if [ ! -d "$results_dir" ]; then
    mkdir "$results_dir"
    echo "Folder '$results_dir' created."
else
    echo "Folder '$results_dir' already exists."
fi

if [ "$test_set" = "gsm8k" ]; then
    echo "Usage: $1"

    python -u experiments/main.py \
            --config="experiments/configs/individual_${model}.py" \
            --config.attack="gcg" \
            --config.train_data="data/gsm8k.jsonl" \
            --config.result_prefix="experiments/results/${model}_gsm8k_${few_shot}_shots" \
            --config.data_offset=0 \
            --config.n_steps=$n_steps \
            --config.test_steps=1 \
            --config.batch_size=$batch_size \
            --config.test_set=$test_set \
            --config.few_shot=$few_shot \
    done
fi

if [ "$test_set" = "mmlu" ]; then
    echo "Usage: $1"

    python -u experiments/main.py \
            --config="experiments/configs/individual_${model}.py" \
            --config.attack="gcg" \
            --config.train_data="data/mmlu" \
            --config.result_prefix="experiments/results/${model}_mmlu_${few_shot}_shots" \
            --config.data_offset=0 \
            --config.n_steps=$n_steps \
            --config.test_steps=1 \
            --config.batch_size=$batch_size \
            --config.test_set=$test_set \
            --config.few_shot=$few_shot \
    done
fi

if [ "$test_set" = "math" ]; then
    echo "Usage: $1"

    python -u experiments/main.py \
            --config="experiments/configs/individual_${model}.py" \
            --config.attack="gcg" \
            --config.train_data="data/math.json" \
            --config.result_prefix="experiments/results/${model}_math_${few_shot}_shots" \
            --config.data_offset=0 \
            --config.n_steps=$n_steps \
            --config.test_steps=1 \
            --config.batch_size=$batch_size \
            --config.test_set=$test_set \
            --config.few_shot=$few_shot \
    done
fi

if [ "$test_set" = "multiarith" ]; then
    echo "Usage: $1"

    python -u experiments/main.py \
            --config="experiments/configs/individual_${model}.py" \
            --config.attack="gcg" \
            --config.train_data="data/multiarith.json" \
            --config.result_prefix="experiments/results/${model}_multiarith_${few_shot}_shots" \
            --config.data_offset=0 \
            --config.n_steps=$n_steps \
            --config.test_steps=1 \
            --config.batch_size=$batch_size \
            --config.test_set=$test_set \
            --config.few_shot=$few_shot \
    done
fi