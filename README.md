## Kharagpur Data Science Hackathon 2025 — Research Paper Evaluation

### Team HACKTIVATE
- Abhijeet Mate (Team Lead)
- Harshal Malani

---

### Overview
This project evaluates research papers (PDF) using an LLM-driven multi-agent system and provides a structured review with publishability judgment and a suggested target conference. It is built for the Kharagpur Data Science Hackathon 2025 by Team HACKTIVATE.

---

### How it works (brief)
- Upload a PDF in the Streamlit app.
- The system splits the paper, analyzes multiple aspects (significance, methodology, presentation, strengths/weaknesses, justification, detailed feedback), and aggregates them into a final evaluation.
- If the paper is deemed publishable, a conference recommender compares fit across top venues (e.g., CVPR, NeurIPS, EMNLP, KDD, TMLR, DAA) and returns a suggested venue with a confidence score and rationale.
- Results can be downloaded as PDF/JSON/CSV. Evaluations can be persisted if a database is configured.

---

### Project structure
- `app.py`: Streamlit UI for interactive single-paper evaluation and downloads.
- `FinalSystem.py`: Batch driver for processing papers programmatically.
- `System.py`: Core orchestration — classification pipeline, aspect aggregation, final scoring, and conference discussion/decision.
- `Agents.py`: Thin wrappers that bind prompts to the LLM for specific tasks.
- `Prompts.py`: Prompt templates for classification, aspect summaries, output schema, and conference selection.
- `ThemesAndContext.py`: Conference-specific themes and context used by the recommender.
- `PDFManager.py`: PDF I/O, chunking, and splitting utilities.
- `Utility.py`: Data models (e.g., `PaperEvaluation`) and model/LLM helpers.
- `RichLogger.py`: Minimal logging utilities.
- `deepseek_locally.py`: Optional local-model helper (if used).
- `requirements.txt`: Python dependencies.

---

### Quickstart
1) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows PowerShell
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Run the app
```bash
streamlit run app.py
```

Notes:
- Processing can take 20–55 minutes depending on PDF length/complexity.
- Smaller PDFs process faster; very large files may take significantly longer.

---

### Acknowledgements
Built for the Kharagpur Data Science Hackathon 2025 by Team HACKTIVATE.

---

### License
MIT License
