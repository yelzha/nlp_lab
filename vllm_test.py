from vllm import LLM, SamplingParams
prompts = [
    "A robe takes 2 bolts of blue fiber and half that much white fiber. How many bolts in total does it take?",
    "James decides to run 3 sprints 3 times a week.  He runs 60 meters each sprint.  How many total meters does he run a week?",
    "Claire makes a 3 egg omelet every morning for breakfast.  How many dozens of eggs will she eat in 4 weeks?",
    "Gretchen has 110 coins. There are 30 more gold coins than silver coins. How many gold coins does Gretchen have?",
] * 25
# Total 100 question, and 50 Agents

sampling_params = SamplingParams(n=50, temperature=0.7, top_p=0.9, max_tokens=2048)
llm = LLM(model="Qwen/Qwen3-4B")
responses = llm.generate(prompts, sampling_params)


for response in responses:
    print("----------------------------------------------------")
    print(response.outputs)
    print("----------------------------------------------------")

print("++++++++++++++++++++++++++++++++++++++++")
