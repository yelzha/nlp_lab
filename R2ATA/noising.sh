#!/bin/bash

export WANDB_MODE=disabled

# Optionally set the cache for transformers
# export TRANSFORMERS_CACHE='YOUR_PATH/huggingface'

# Read arguments
export model=$1                # 'mistral', 'gemma' or 'llama'
export test_set=$2              # 'gsm8k', 'mmlu'
export n_train_data=$3         # sampled number of each topic
export n_steps=$4              # number of edits
export batch_size=$5           # batch size
export few_shot=$6

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

    python -u ../main.py \
            --config="experiments/configs/individual_${model}.py" \
            --config.attack="gcg" \
            --config.train_data="data/gsm8k.jsonl" \
            --config.result_prefix="experiments/results/${model}_gsm8k_${few_shot}_shots" \
            --config.n_train_data=$n_train_data \
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

    python -u ../main.py \
            --config="experiments/configs/individual_${model}.py" \
            --config.attack="gcg" \
            --config.train_data="data/mmlu.json" \
            --config.result_prefix="experiments/results/${model}_mmlu_${few_shot}_shots" \
            --config.n_train_data=$n_train_data \
            --config.data_offset=0 \
            --config.n_steps=$n_steps \
            --config.test_steps=1 \
            --config.batch_size=$batch_size \
            --config.test_set=$test_set \
            --config.few_shot=$few_shot \
    done
fi