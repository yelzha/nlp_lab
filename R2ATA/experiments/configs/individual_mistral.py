import os

os.sys.path.append("..")
from configs.template import get_config as default_config


def get_config():
    config = default_config()

    config.result_prefix = 'results/individual_mistral'

    config.tokenizer_paths = ["mistralai/Mistral-7B-v0.3"]
    config.model_paths = ["mistralai/Mistral-7B-v0.3"]

    config.conversation_templates=['mistral']

    return config