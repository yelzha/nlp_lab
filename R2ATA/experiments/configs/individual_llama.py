import os

os.sys.path.append("..")
from configs.template import get_config as default_config


def get_config():
    config = default_config()

    config.result_prefix = 'results/llama3/'

    config.tokenizer_paths = ["meta-llama/Meta-Llama-3-8B-Instruct"]
    config.model_paths = ["meta-llama/Meta-Llama-3-8B-Instruct"]

    config.conversation_templates = ['llama-3']  # must match a template in fastchat.model.get_conversation_template

    return config
