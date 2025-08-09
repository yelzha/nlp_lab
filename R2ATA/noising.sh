#!/bin/bash
#SBATCH --partition=A40short
#SBATCH --time=07:59:59
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
            --config.train_data="data/mmlu.json" \
            --config.result_prefix="experiments/results/${model}_mmlu_${few_shot}_shots" \
            --config.data_offset=0 \
            --config.n_steps=$n_steps \
            --config.test_steps=1 \
            --config.batch_size=$batch_size \
            --config.test_set=$test_set \
            --config.few_shot=$few_shot \
    done
fi