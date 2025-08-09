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
 
### 2.2 Wikitypo, r2ata
- **Status:** Pengind  
- **Goal:** Add noising to the dataset
- **Target:** Achieve generated results

---

## 2. Ongoing & Upcoming Tasks

## Experiments Overview

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
| Ollama Optimization          |   Done   | Focus on reducing latency -> VLLM migration          |
| Prompting Fixes       |   Done   | Changed fully for all datasets    |
| WikiTypo(2025) Noising       |   Done   | Requires initial implementation    |
| R2ATA Noising       |   Todo   | Requires initial implementation    |
| Gemma Fix for VLLM       |   Todo   | Requires initial implementation    |
| Full Experiments             |   Todo   | Will run for over a week           |
| Report & Visualization       |   Todo   | Final stage                        |

---

## Notes
- All code and runtime logs are stored on Bender under `/home/s06zyelt/nlp_lab/`.
- Environment dependencies and setup steps are documented in `README.md`.


```commandline

module load Miniforge3
module load git/2.41.0-GCCcore-12.3.0-nodocs
conda activate /home/s06zyelt/nlp_lab/env
huggingface-cli download meta-llama/Llama-3.1-8B-Instruct
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.3
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

```commandline

```
