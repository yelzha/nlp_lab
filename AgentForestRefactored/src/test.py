from gsm_task import GSM8K

solver = GSM8K(1, "qwen3:4B", temperature=0.2, top_p=1, dtype="clean")

question_datas = solver.get_question_datas()

print(len(question_datas))