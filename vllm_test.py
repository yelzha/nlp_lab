# import requests
# import json
# import time
# import os
#
#
# llm_ip = os.getenv('LLM_IP')
#
# url = f"http://{llm_ip}/v1/completions"
# headers = {"Content-Type": "application/json"}
# data = {
#     "model": "Qwen/Qwen3-4B",
#     "prompt": "Hello, my name is",
#     "max_tokens": 50,
#     "temperature": 0.7,
#     "top_p": 0.9,
#     "stream": False
# }
import openai
import os

llm_ip = os.getenv('LLM_IP')
answer_context = [
    "A robe takes 2 bolts of blue fiber and half that much white fiber. How many bolts in total does it take?"
]

openai.api_base = "http://{}/v1".format(llm_ip)
openai.api_key = "none"
openai.api_type = "openai"
openai.api_version = ""
completion = openai.ChatCompletion.create(
    model="Qwen/Qwen3-4B",
    messages=answer_context,
    n=5,
    max_tokens=1024,
    temperature=1.0,
)
print("Completion result:", completion)

# from vllm import LLM, SamplingParams
# prompts = [
#     "Mexico is famous for ",
#     "The largest country in the world is ",
# ]
#
# sampling_params = SamplingParams(temperature=0.7, top_p=0.9)
# llm = LLM(model="Qwen/Qwen3-4B")
# responses = llm.generate(prompts, sampling_params)
#
# for response in responses:
#     print(response.outputs[0].text)

