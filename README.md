# Kharagpur Data Science Hackathon 2025 - Research Paper Analysis Tool
---
## Teeam Hactivate 

- Abhijeet Mate (Team Leader)
- Harshal Malani 

---

## Prerequisites

- Python 3.8 or higher
- Groq API key ([Get it here](https://console.groq.com/login))
- Active internet connection

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create a Python virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:

**For Unix/macOS:**
```bash
source .venv/bin/activate
```

**For Windows:**
```bash
.venv\Scripts\activate
```

4. Install dependencies:

**Quiet installation:**
```bash
pip install -qU -r requirements.txt
```

**Standard installation:**
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Configure the application:
   - Enter your Groq API key in the sidebar
   - Upload your research paper
   - Wait for 25-45 minutes while the report is generated

## Features

- Research paper analysis using Groq's LLM
- Well-organized report generation
- User-friendly Streamlit interface

## Processing Time

The report generation typically takes between 25-45 minutes, depending on the paper's length and complexity.
