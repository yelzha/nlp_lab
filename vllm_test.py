import requests
import json
import time
import os


llm_ip = os.getenv('LLM_IP')

url = f"http://{llm_ip}/v1/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model": "Qwen/Qwen3-4B",
    "prompt": "Hello, my name is",
    "max_tokens": 50,
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": False
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    print("Request successful!")
    print("Response status code:", response.status_code)
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))

    # Optional: Test with streaming
    print("\nTesting streaming response:")
    data["stream"] = True
    response_stream = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    response_stream.raise_for_status()
    for chunk in response_stream.iter_content(chunk_size=None):
        if chunk:
            try:
                # Decode chunk, remove 'data: ' prefix, and parse JSON
                lines = chunk.decode('utf-8').splitlines()
                for line in lines:
                    if line.startswith("data: "):
                        json_data = line[len("data: "):]
                        if json_data.strip() == "[DONE]":
                            print("[STREAM DONE]")
                            break
                        parsed_data = json.loads(json_data)
                        print(json.dumps(parsed_data, indent=2))
            except json.JSONDecodeError:
                print(f"Could not decode JSON from chunk: {chunk.decode('utf-8')}")
            except Exception as e:
                print(f"Error processing stream chunk: {e}")

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to vLLM server at {url}. Is it running? Error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout Error: Request to vLLM server timed out. Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")