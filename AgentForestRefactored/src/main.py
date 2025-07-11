# main.py
import sys
import os
import random
import json
import pandas as pd
from datetime import datetime  # Import datetime for generating a timestamp if SLURM_JOB_ID is not set
from code_completion_task import CodeCompletion
from mmlu_task import MMLU
from math_task import MATH
from chess_task import CHESS
from gsm_task import GSM8K
from human_eval.data import write_jsonl

PART = int(sys.argv[1])
SUBSET = int(sys.argv[2])
MODEL = sys.argv[3]  # Adjusted sys.argv index
DTYPE = sys.argv[4]  # Adjusted sys.argv index
QUESTION_TYPE = sys.argv[5]  # Adjusted sys.argv index
TEMPERATURE = float(sys.argv[6])  # Adjusted sys.argv index
TOP_P = float(sys.argv[7])  # Adjusted sys.argv index


def main():
    random.seed(0)

    # Define the K values for voting. The maximum value in this list
    # determines the total number of agents to initialize for response generation.
    K_values = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    # K_values = list(range(1, 51))
    # Initialize the solver with the maximum number of agents (e.g., 50)
    # as all agent responses will be generated in a single batch.
    max_agents_for_init = K_values[-1]

    # Fetch SLURM_JOB_ID from environment, or use a timestamp for local runs
    slurm_job_id = os.getenv('SLURM_JOB_ID', datetime.now().strftime('%Y%m%d_%H%M%S_local_run'))

    # Base directory for all logs related to this job/run
    base_log_dir = f"../../experiments/{DTYPE}/{MODEL}"
    os.makedirs(base_log_dir, exist_ok=True)

    if QUESTION_TYPE == "human-eval":
        solver = CodeCompletion(max_agents_for_init, MODEL, temperature=TEMPERATURE, top_p=TOP_P, dtype=DTYPE)
    elif QUESTION_TYPE == "mmlu":
        solver = MMLU(max_agents_for_init, MODEL, temperature=TEMPERATURE, top_p=TOP_P, dtype=DTYPE)
    elif QUESTION_TYPE == "math":
        solver = MATH(max_agents_for_init, MODEL, temperature=TEMPERATURE, top_p=TOP_P, dtype=DTYPE)
    elif QUESTION_TYPE == "chess":
        solver = CHESS(max_agents_for_init, MODEL, temperature=TEMPERATURE, top_p=TOP_P, dtype=DTYPE)
    elif QUESTION_TYPE == "gsm":
        solver = GSM8K(max_agents_for_init, MODEL, temperature=TEMPERATURE, top_p=TOP_P, dtype=DTYPE)
    else:
        raise NotImplementedError("Error question type")

    results_human_eval_for_max_K = []  # Stores human-eval completions for the max K value
    total_prompt_tokens, total_completion_tokens = 0, 0

    # total_records will store all results (for all K values) for the current PART*SUBSET
    total_records_dict = {}
    question_datas = solver.get_question_datas()

    print("=============================================================")
    print(f"PART->SUBSET = [{PART * SUBSET}, {(PART + 1) * SUBSET}]...")
    print("=============================================================")

    for task_id, question_data in enumerate(question_datas):
        if task_id < PART * SUBSET or task_id >= (PART + 1) * SUBSET:
            continue
        print("current task_id start: ", task_id, flush=True)

        # Call forward to get all agent completions and parsed answers
        result_dict = solver.forward(question_data)
        ground_truth = question_data["ground_truth"]

        all_answers = result_dict["answers"]
        total_prompt_tokens += result_dict["total_prompt_tokens"]
        total_completion_tokens += result_dict["total_completion_tokens"]

        # Process and store results for each K value for the current question
        for K in K_values:
            if K not in total_records_dict:
                total_records_dict[K] = []
            # Ensure K does not exceed the number of available answers
            current_K = min(K, len(all_answers))
            subset_answers = all_answers[:current_K]

            one_record = {}
            # Add original question data
            for k, v in question_data.items():
                one_record[k] = v
            for k, v in result_dict.items():
                if isinstance(v, list):
                    for i, sub_v in enumerate(v):
                        new_k = k + f"_{i}"
                        one_record[new_k] = sub_v
                else:
                    one_record[k] = v

            # Get the final answer for the current K using the solver's voting method
            activated_indices = [i for i in range(K)]
            final_answer_for_K = solver.get_final_answer(activated_indices, one_record)

            # Add the final answer for the current K
            one_record[f"final_answer"] = final_answer_for_K

            total_records_dict[K].append(one_record)  # Add to overall list

            # For human-eval, store the completion for the largest K (max_agents_for_init)
            if QUESTION_TYPE == "human-eval" and K == max_agents_for_init:
                results_human_eval_for_max_K.append(
                    {"task_id": question_data["task_id"], "completion": final_answer_for_K})

            if QUESTION_TYPE != "human-eval":
                tmp_df = pd.DataFrame(total_records_dict[K])
                perf = solver.evaluation(tmp_df)
                print(f"{K} Agents final_res: {final_answer_for_K}, ground_truth: {ground_truth}, perf: {perf}", flush=True)

        print("current task_id end: ", task_id, flush=True)
        print("************************", flush=True)
        print(f"Total prompt tokens: {total_prompt_tokens}, Total completion tokens: {total_completion_tokens}", flush=True)

    # Save results for each K value to separate files and directories
    print("\n--- Saving Results for Each K Value ---")
    for K in K_values:
        # Generate K-specific EXP_NAME and DIR_NAME
        K_EXP_NAME = f"{QUESTION_TYPE}_{K}_agents_part_{PART}"
        K_DIR_NAME = os.path.join(base_log_dir, f"log_{QUESTION_TYPE}_{DTYPE}_{K}_agents")  # Create sub-directory for each K
        os.makedirs(K_DIR_NAME, exist_ok=True)

        # Filter DataFrame for the current K value
        df_k = pd.DataFrame(total_records_dict[K]).copy()

        # Save to CSV
        csv_path = os.path.join(K_DIR_NAME, f"{K_EXP_NAME}.csv")
        df_k.to_csv(csv_path, index=False)
        print(f"Saved CSV for K={K} to: {csv_path}")

        # Save to JSONL (one JSON object per line)
        json_path = os.path.join(K_DIR_NAME, f"{K_EXP_NAME}.json")
        with open(json_path, 'w') as f:
            for record in df_k.to_dict(orient='records'):
                f.write(json.dumps(record) + '\n')
        print(f"Saved JSON for K={K} to: {json_path}")

        # Handle human-eval specific .jsonl output for the max K value
        if QUESTION_TYPE == "human-eval" and K == max_agents_for_init:
            human_eval_jsonl_path = os.path.join(K_DIR_NAME, f'{K_EXP_NAME}.jsonl')
            write_jsonl(human_eval_jsonl_path, results_human_eval_for_max_K)
            print(f"Saved Human-Eval JSONL for K={K} to: {human_eval_jsonl_path}")

    # Evaluate performance for each K value (using the full df_all_records for filtering)
    print("\n--- Final Evaluation for Each K Value ---")
    for K in K_values:
        # Filter DataFrame for the current K value
        df_k_eval = pd.DataFrame(total_records_dict[K]).copy()
        # Rename the specific K column to 'final_answer' for the evaluation function
        df_k_eval.rename(columns={f"final_answer_k{K}": "final_answer"}, inplace=True)

        # Ensure 'ground_truth' and 'final_answer' columns exist for evaluation
        if "ground_truth" in df_k_eval.columns and "final_answer" in df_k_eval.columns:
            perf = solver.evaluation(df_k_eval)
            print(f"Part {PART} final evaluation for K={K}: {perf}")
        else:
            print(f"Cannot evaluate K={K}: Missing 'ground_truth' or 'final_answer' column in filtered DataFrame.")


if __name__ == "__main__":
    main()
