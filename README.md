# TO DO
- [x] Have implemented, prepared and tested AgentFores code on Bender (changed some parts due to issues), and it took 2 hours 47 minutes for clean dataset with solo agent.
- [ ] Solve optimization problem of Ollama on Bender (usually it takes 5-20 seconds to answer to a question) 
- [ ] Implement and test WikiTypo(2025) noising algorithms
- [ ] Run all experiments, and collect results (estimated more than 1 week to run all codes)
- [ ] Write a report and visualize the results

# instructions
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
