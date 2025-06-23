import requests

# old port: 11434

response = requests.post(
    'http://localhost:11500/api/generate',
    json={
        'model': 'qwen3:14b',
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
