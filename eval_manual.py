import os
import subprocess
import sys

# --- Constants for the Experiment ---
# These parameters are hardcoded as requested.
MODEL = "Mistral-7B-Instruct-v0.3"
QTYPE = "gsm"
DTYPE = "clean"  # Assuming DTYPES="clean" refers to a single DTYPE
SUBSET_NUM = 100
TEMPERATURE = 1
TOP_P = 1
VLLM_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

# --- Script Configuration ---
# K_VALUES remain the same as in the original Bash script
K_VALUES = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

# Get MAIN_DIRECTORY from environment variables.
# If not set, it defaults to the current working directory.
MAIN_DIRECTORY = os.getcwd()

# Construct the base directory name using os.path.join for cross-platform compatibility
BASE_DIR_NAME = os.path.join(MAIN_DIRECTORY, "experiments", DTYPE, MODEL, QTYPE)


# --- Utility Function for Subprocess Calls ---
def run_command(command, description):
    """Executes a command and handles potential errors."""
    print(f"\nExecuting: {' '.join(command)}")
    try:
        # We use sys.executable to ensure the current Python interpreter is used for `main.py` and `evaluation.py`
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"{description} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\nError during {description}: {e}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"\nError: Command or script not found. Ensure Python and the required scripts are accessible.",
              file=sys.stderr)
        sys.exit(1)


# --- Main Execution ---
def main():
    # --- Run evaluation.py for each agent ---
    print("\nAll main.py runs done. Starting evaluation...")
    for agent in K_VALUES:
        # print(f"AGENT {agent}: Evaluating...")

        # Construct the directory name for the evaluation logs
        dir_name = os.path.join(BASE_DIR_NAME, f"log_{QTYPE}_{DTYPE}_{agent}_agents")
        src_path = os.path.join(MAIN_DIRECTORY, "AgentForestRefactored", "src", "evaluation.py")

        # # Construct the command for evaluation.py
        # command = [
        #     sys.executable,
        #     src_path,
        #     dir_name,
        #     QTYPE
        # ]
        #
        # run_command(command, f"evaluation.py for AGENT {agent}")
        with open(os.path.join(dir_name, "final_perf.txt")) as f:
            lines = f.readlines()
            print(f"AGENT {agent}:", lines[0])

    print("\nScript finished successfully.")


if __name__ == "__main__":
    main()