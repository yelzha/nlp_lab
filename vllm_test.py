# test_gemma.py
import os
from vllm import LLM, SamplingParams

# Define the model name. This should match what you pass to vLLM.
# It can also be read from an environment variable, similar to your SLURM script.
# For direct testing, we'll hardcode it or use an env var if set.
MODEL_NAME = os.environ.get("VLLM_MODEL_NAME", "google/gemma-3-4b-it")

print(f"Loading model: {MODEL_NAME}...")

# Create a sampling_params object.
# You can adjust these parameters as needed for your test.
sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=100)

# Create an LLM. This will download the model if not cached.
# For local models, 'model' should be the path to the model directory.
# For Hugging Face models, it's the model ID.
llm = LLM(model=MODEL_NAME, gpu_memory_utilization=0.9) # Adjust gpu_memory_utilization as needed

# Define a simple prompt for testing
prompts = [
    "Write a short, engaging story about a brave knight and a mischievous dragon.",
    "Explain the concept of quantum entanglement in simple terms.",
    "What is the capital of France?",
]

print("\nGenerating responses...")
outputs = llm.generate(prompts, sampling_params)

# Print the outputs
for i, output in enumerate(outputs):
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"--- Prompt {i+1} ---")
    print(f"Prompt: {prompt!r}")
    print(f"Generated text: {generated_text!r}")
    print("-" * 30)

print("\nTest complete.")