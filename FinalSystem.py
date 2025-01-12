from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from Utility import ModelManager, PaperEvaluation
from System import SystemSTORM, SystemClassification
from ThemesAndContext import ThemesAndContext
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

array_api_keys_and_paper_location=[
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P098.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P099.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P100.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P101.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P102.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P103.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P104.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P105.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P106.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P107.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P108.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P109.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P110.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P111.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P112.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P113.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P114.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P115.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P116.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P117.pdf"]),
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

def save_evaluation(paper_id, publishable, conference, justification, conference_rationale):
    document = {
        "paper_id": paper_id,
        "publishable": publishable,
        "conference": conference,
        "justification": justification,
        "conference_rationale": conference_rationale,
    }
    collection.insert_one(document)  
        
def process_papers(api_key, paper_locations):
    print(f"processing with api_key : {api_key}")
    llm = ModelManager.get_groq_llm(model_name="llama-3.1-8b-instant", api_key=api_key)
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
            save_evaluation(paper_id, False, "", output_model.justification, "")
            print("Evaluation Saved Successfully with not publishable")
        else:
            conference_decision = conference_system.discuss_and_decide(report_of_paper=report_summary)
            if conference_decision:
                save_evaluation(
                    paper_id,
                    True,
                    conference_decision["conference"],
                    output_model.justification,
                    conference_decision["justification"],
                )
                print("Evaluation Saved Successfully  publishable")
        time.sleep(90)  # Simulate 1.5 minutes per paper


def main():
    with ThreadPoolExecutor(max_workers=19) as executor:
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
    