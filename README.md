# Project To-Do List

---

## 1. Completed Tasks

### 1.1 AEDA Implementation
- **Status:** Completed  
- **Description:** Successfully implemented and tested simplistic version of AEDA using Python code.
- **Outcome:** Works as expected.

### 1.2 Local LLM Integration (Ollama + Python)
- **Status:** Completed  
- **Description:** Successfully installed and tested Ollama with Python code execution on Bender using local LLMs.  
- **Outcome:** Local inference working as expected.

### 1.3 AgentFores: Implementation and Testing
- **Status:** Completed  
- **Description:** Adapted, implemented, and validated the AgentFores codebase.  
- **Adjustments:** Code was modified to address compatibility issues on Bender.  
- **Benchmark Result:**  
  - Runtime: **2h 47m** on clean dataset  
  - Mode: Solo Agent Execution
  - Issues: Not optimized for Parallel Inference and some problems with GPU
 
### 2.1 Ollama Optimization -> migration to VLLM Framework
- **Status:** Completed  
- **Goal:** Improve Ollama’s response time on Bender.  
- **Current Performance:** ~5–20 seconds per query (qwen3:4B full mode)
- **Target:** Achieve stable, low-latency inference (<5s preferred)
- **Results:** Good performance for N Agents with the 16-20 seconds per n of query.

---

## 2. Ongoing & Upcoming Tasks

## Experiments Overview

| Noise Type     | Model        | Agent N | Status     | Accuracy           |  Notes           |
|----------------|--------------|---------|------------|--------------------|-----------------------|
| clean          | qwen3:4B     | 1       | Completed  | 0.8148148148148148 |  N/A  |
| clean          | qwen3:4B     | 5       | Completed  | 0.9095074455899198 | N/A     |
| clean          | qwen3:4B     | 10      | Completed  | 0.9156166475754105 |  N/A   |
| clean          | qwen3:4B     | 15      | Pending    | 0.9201985490645285 |  N/A |
| clean          | qwen3:4B     | 20      | Pending    | 0.9232531500572738 |  N/A |
| clean          | qwen3:4B     | 25      | Pending    | 0.9270714012982054 |  N/A|
| clean          | qwen3:4B     | 30      | Pending    | 0.928598701794578  |  N/A|
| clean          | qwen3:4B     | 35      | Pending    | 0.9278350515463918 |  N/A |
| clean          | qwen3:4B     | 40      | Pending    | 0.930889652539137  |  N/A|
| clean          | qwen3:4B     | 45      | Pending    | 0.9301260022909508 |  N/A|
| clean          | qwen3:4B     | 50      | Pending    | 0.930889652539137  |  N/A |
|---|---|---|---|---|---|
| clean | qwen3:14B | 1 | Completed | 0.868081880212282 | N/A |
| clean | qwen3:14B | 5 | Completed | 0.9203942380591357 | N/A |
| clean | qwen3:14B | 10 | Completed | 0.9317664897649734 | N/A |
| clean | qwen3:14B | 15 | Completed | 0.9325246398786959 | N/A |
| clean | qwen3:14B | 20 | Completed | 0.934040940106141 | N/A |
| clean | qwen3:14B | 25 | Completed | 0.9347990902198635 | N/A |
| clean | qwen3:14B | 30 | Completed | 0.934040940106141 | N/A |
| clean | qwen3:14B | 35 | Completed | 0.9332827899924185 | N/A |
| clean | qwen3:14B | 40 | Completed | 0.935557240333586 | N/A |
| clean | qwen3:14B | 45 | Completed | 0.935557240333586 | N/A |
| clean | qwen3:14B | 50 | Completed | 0.935557240333586 | N/A |
|---|---|---|---|---|---|
| clean | Llama-3.1-8B-Instruct | 1 | Completed | 0.6315390447308568 | N/A |
| clean | Llama-3.1-8B-Instruct | 5 | Completed | 0.8385140257771039 | N/A |
| clean | Llama-3.1-8B-Instruct | 10 | Completed | 0.8953752843062927 | N/A |
| clean | Llama-3.1-8B-Instruct | 15 | Completed | 0.9128127369219106 | N/A |
| clean | Llama-3.1-8B-Instruct | 20 | Completed | 0.9150871872630781 | N/A |
| clean | Llama-3.1-8B-Instruct | 25 | Completed | 0.9173616376042456 | N/A |
| clean | Llama-3.1-8B-Instruct | 30 | Completed | 0.9188779378316907 | N/A |
| clean | Llama-3.1-8B-Instruct | 35 | Completed | 0.9226686884003032 | N/A |
| clean | Llama-3.1-8B-Instruct | 40 | Completed | 0.9211523881728583 | N/A |
| clean | Llama-3.1-8B-Instruct | 45 | Completed | 0.9219105382865808 | N/A |
| clean | Llama-3.1-8B-Instruct | 50 | Completed | 0.9211523881728583 | N/A |
|---|---|---|---|---|---|
| clean | Mistral-7B-Instruct-v0.3 | 1 | Completed | 0.4200164068908942 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 5 | Completed | 0.5972108285479901 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 10 | Completed | 0.6808859721082855 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 15 | Completed | 0.7235438884331419 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 20 | Completed | 0.7506152584085316 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 25 | Completed | 0.7547169811320755 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 30 | Completed | 0.7579983593109105 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 35 | Completed | 0.7588187038556193 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 40 | Completed | 0.7629204265791633 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 45 | Completed | 0.7703035274815423 | N/A |
| clean | Mistral-7B-Instruct-v0.3 | 50 | Completed | 0.7768662838392125 | N/A |

<img width="2379" height="1380" alt="image" src="https://github.com/user-attachments/assets/616ee6c1-825c-4788-a214-3ff7fe76391a" />

### 2.2 Experimental Runs & Data Collection
- **Status:** Pending  
- **Description:** Execute all planned experimental configurations (Clean & AEDA & WikiTypo -> 1-50 Agents).  
- **Estimated Duration:** **1-3+ week** of continuous runtime  
- **Deliverables:** Logs, metrics, performance data for all models and settings.

### 2.3 Report & Visualization
- **Status:** Pending  
- **Goal:** Compile results into a detailed report with clear visualizations.  
- **Tools Suggested:** Python (Matplotlib/Plotly), Pandas, LaTeX for formatting.

---

## Timeline Overview

| Task                         | Status   | ETA / Notes                        |
|------------------------------|----------|------------------------------------|
| Ollama + Python Integration  |   Done   | Complete                           |
| AgentFores Implementation    |   Done   | Runtime measured: 2h 47m           |
| Ollama Optimization          |   Todo   | Focus on reducing latency          |
| WikiTypo(2025) Noising       |   Todo   | Requires initial implementation    |
| Full Experiments             |   Todo   | Will run for over a week           |
| Report & Visualization       |   Todo   | Final stage                        |

---

## Notes
- All code and runtime logs are stored on Bender under `/home/s06zyelt/nlp_lab/`.
- Environment dependencies and setup steps are documented in `README.md`.


```commandline
huggingface-cli download model
```


## Setup Steps
```
=========initialization start=========
======================================
mkdir -p ~/ollama/bin

curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz

tar -xzf ollama-linux-amd64.tgz -C ~/ollama

echo 'export PATH="$HOME/ollama/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

ollama --version









# double check this place, maybe some mistakes / errors

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
conda create -p /home/s06zyelt/nlp_lab/env python=3.10 -y
source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

cd nlp_lab
sbatch run_test.sh

==========initialization end==========
======================================
```






```
==========code test start=============
======================================

# ~/nlp_lab/run_test.sh:
#!/bin/bash
#SBATCH --partition=A40devel
#SBATCH --time=0:05:00
#SBATCH --gpus=1
#SBATCH --output=slurm_output.txt   # Log everything here

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs


#conda create -p /home/s06zyelt/nlp_lab/env python=3.10 -y
source /software/easybuild-INTEL_A40/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /home/s06zyelt/nlp_lab/env

pip install numpy pandas
pip install openai==0.28.1
pip install sacrebleu
pip install git+https://github.com/openai/human-eval.git

python -c "import numpy, pandas, openai; print('All good')"
python -c "from human_eval.data import read_problems; print('human_eval works')"



export OLLAMA_HOST=127.0.0.1:11500
ollama serve &
sleep 5
ollama run qwen3:0.6b || true

python ollama_test.py

echo "Finished!!!"








# ~/nlp_lab/ollama_test.py:
import requests

# old port: 11434

response = requests.post(
    'http://localhost:11500/api/generate',
    json={
        'model': 'qwen3:0.6b',
        'prompt': 'What is the capital of France?',
        'stream': False
    }
)

result = response.json()['response']

# Print to console (optional)
print(result)

# Save to a text file
with open('output.txt', 'w') as f:
    f.write(result)

==========code test end===============
======================================
```
