from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from Utility import ModelManager, PaperEvaluation
from System import SystemSTORM, SystemClassification
from ThemesAndContext import ThemesAndContext
import os
import time

# MongoDB connection
MONGO_URI = "mongodb+srv://malaniharshal95:1h2a3r4s@hactivate.dnymy.mongodb.net/?retryWrites=true&w=majority&appName=Hactivate"

try:
    client = MongoClient(MONGO_URI)
    db = client["paper_evaluations"]
    collection = db["paper_evaluations"]
except Exception as e:
    print("Failed to connect to database. Error:", e)
    raise e

# API keys and paper locations
array_api_keys_and_paper_location=[
    ("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", ["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/R011.pdf"])
]


def create_report_of_paper(output_model: PaperEvaluation) -> str:
    return " ".join([
        output_model.significance,
        output_model.methodology,
        output_model.presentation,
        output_model.justification,
        output_model.major_strengths,
        output_model.major_weaknesses,
        output_model.detailed_feedback,
    ])

def save_evaluation(paper_id, publishable, justification, significance, methodology, presentation, confidence_score, score, major_strengths, major_weaknesses, detailed_feedback, conference_score, conference_rationale, conference):
    document = {
        "paper_id": paper_id,
        "publishable": publishable,
        "conference": conference,
        "justification": justification,
        "significance": significance,
        "methodology": methodology,
        "presentation": presentation,
        "confidence_score": confidence_score,
        "score": score,
        "major_strengths": major_strengths,
        "major_weaknesses": major_weaknesses,
        "detailed_feedback": detailed_feedback,
        "conference_score": conference_score,
        "conference_rationale": conference_rationale,
    }
    collection.insert_one(document)

def process_papers(api_key, paper_locations):
    print(f"Processing with API key: {api_key}")
    llm = ModelManager.get_ollama_llm(model_name="llama-3.1-8b-instant", api_key=api_key)
    classification_system = SystemClassification(llm=llm, debug=True)
    conference_system = SystemSTORM(
        llm=llm,
        cvpr_theme=ThemesAndContext.cvpr_theme(),
        cvpr_context=ThemesAndContext.cvpr_context(),
        neur_ips_theme=ThemesAndContext.neur_ips_theme(),
        neur_ips_context=ThemesAndContext.neur_ips_context(),
        emnlp_theme=ThemesAndContext.emnlp_theme(),
        emnlp_context=ThemesAndContext.emnlp_context(),
        kdd_theme=ThemesAndContext.kdd_theme(),
        kdd_context=ThemesAndContext.kdd_context(),
        tmlr_theme=ThemesAndContext.tmlr_theme(),
        tmlr_context=ThemesAndContext.tmlr_context(),
        daa_theme=ThemesAndContext.daa_theme(),
        daa_context=ThemesAndContext.daa_context(),
        wait_time=10,
        debug=True,
    )

    for paper_path in paper_locations:
        print(f"Processing {paper_path} with API key {api_key}")
        output_model = classification_system.classify_paper(path_to_pdf=paper_path)

        report_summary = create_report_of_paper(output_model)
        
        paper_id = paper_path[-8:]
        paper_id= paper_id[0:4]   
        
        if not output_model.publishable:
            save_evaluation(
                paper_id, False, output_model.justification, output_model.significance, 
                output_model.methodology, output_model.presentation, output_model.confidence_score, 
                output_model.score, output_model.major_strengths, output_model.major_weaknesses, 
                output_model.detailed_feedback, 0, "", ""
            )
            print(f"Evaluation saved successfully (not publishable) {paper_id}")
        else:
            conference_decision = conference_system.discuss_and_decide(report_of_paper=report_summary)
            if conference_decision:
                save_evaluation(
                    paper_id, True, output_model.justification, output_model.significance, 
                    output_model.methodology, output_model.presentation, output_model.confidence_score, 
                    output_model.score, output_model.major_strengths, output_model.major_weaknesses, 
                    output_model.detailed_feedback, conference_decision["score"], 
                    conference_decision["justification"], conference_decision["conference"]
                )
                print(f"Evaluation saved successfully (publishable).{paper_id}")
        
        os.remove(paper_path)
def main():
    with ThreadPoolExecutor(max_workers=10) as executor: 
        futures = []
        for api_key, paper_locations in array_api_keys_and_paper_location:
            futures.append(executor.submit(process_papers, api_key, paper_locations))

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print("Error occurred:", e)

if __name__ == "__main__":
    main()
