from ml_collections import ConfigDict

def get_config():
    c = ConfigDict()

    # WHICH ATTACK TO RUN
    # This must match a module in llm_attacks/ (e.g., "gbda", "ata", etc.)
    # If unsure, check the repo's llm_attacks directory.
    c.attack = "base.attack_manager"  # placeholder: replace with the attack file that implements step()

    # DATASET SELECTION
    c.test_set = "gsm8k"               # or "bbh" / "mmlu"
    c.train_data = "/PATH/TO/gsm8k_train.jsonl"
    c.n_train_data = 100               # how many items to perturb
    c.few_shot = 0                     # as used in get_goals_and_targets()

    # MODEL + TOKENIZER
    c.tokenizer_paths = ["/PATH/TO/llama-2-7b-chat-hf"]
    c.tokenizer_kwargs = [dict(use_fast=False)]
    c.model_paths = ["/PATH/TO/llama-2-7b-chat-hf"]
    c.model_kwargs = [dict(low_cpu_mem_usage=True, use_cache=True)]
    c.conversation_templates = ["llama-2"]
    c.devices = ["cuda:0"]             # or "cpu" if you must

    # ATTACK HYPERPARAMS
    c.gbda_deterministic = True
    c.lr = 0.1
    c.batch_size = 64
    c.n_steps = 100
    c.topk = 64
    c.temp = 1.0
    c.target_weight = 1.0
    c.control_weight = 0.1
    c.anneal = True
    c.incr_control = True
    c.stop_on_success = True
    c.verbose = True
    c.filter_cand = True
    c.allow_non_ascii = False

    # TRAIN / TEST MODEL SPLIT
    c.num_train_models = 1

    # LOGGING
    c.result_prefix = "results/r2ata"  # output JSON (we’ll also export JSONL)

    return c
