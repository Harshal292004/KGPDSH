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
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P042.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P043.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P043.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P044.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P045.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P046.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P047.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P048.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P049.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P050.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P051.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P052.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P053.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P054.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P055.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P056.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P059.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P060.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P061.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P062.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P063.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P064.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P065.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P066.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P067.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P068.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P069.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P070.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P071.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P072.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P074.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P075.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P076.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P077.pdf"]),
    ("gsk_oYfauHkHFNfv4uSVagDmWGdyb3FY8DmlJbYDRH72smXUa1NgM1CSc",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P078.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P079.pdf"]),
    ("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",["/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P080.pdf","/home/harshal/Desktop/KGPDSH/KGPDSH/papers/P081.pdf"]),
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
        
        paper_id=paper_path[-8]
        paper_id=paper_id[0:4]
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
    