from System import SystemClassification
from Utility import ModelManager

llm=ModelManager.get_ollama_llm()

s=SystemClassification(
    llm,
    debug = True,
    wait_time=0,
    wait_time_per_chunk=0,
    wait_time_for_summary = 0,
    wait_time_per_five_chunk = 0,
    wait_time_per_five_chunk_model= 0,
    wait_time_after_model = 0,
    wait_time_recurrsion= 0,
    split_without_stop_words=False,
    odd_even=False,
    threshold= 16000
)


output_model =s.classify_paper(path_to_pdf="papers/R006.pdf")
