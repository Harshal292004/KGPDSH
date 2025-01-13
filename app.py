import tempfile
import pandas as pd
import time 
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pymongo import MongoClient
from io import BytesIO
from Utility import ModelManager, PaperEvaluation
from System import SystemSTORM, SystemClassification
from ThemesAndContext import ThemesAndContext

# MongoDB connection
try:
    MONGO_URI = st.secrets["MONGO_URI"] 
    client = MongoClient(MONGO_URI)
    db = client["paper_evaluations"]  
    collection = db["paper_evaluations"] 
except Exception as e:
    st.error("Failed to connect to database. Please try again later.")

def generate_pdf(evaluation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    elements.append(Paragraph("Paper Evaluation Report", title_style))
    elements.append(Spacer(1, 20))
    
    sections = [
        ("Research Significance", evaluation.significance),
        ("Methodology Assessment", evaluation.methodology),
        ("Presentation Quality", evaluation.presentation),
        ("Major Strengths", evaluation.major_strengths),
        ("Major Weaknesses", evaluation.major_weaknesses),
        ("Score Justification", evaluation.justification),
        ("Detailed Feedback", evaluation.detailed_feedback)
    ]
    
    for title, content in sections:
        elements.append(Paragraph(title, styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(content, styles['Normal']))
        elements.append(Spacer(1, 20))
    
    scores_data = [
        ['Metric', 'Score'],
        ['Confidence Score', str(evaluation.confidence_score)],
        ['Paper Score', str(evaluation.score)],
        ['Publishable', 'Yes' if evaluation.publishable else 'No']
    ]
    
    scores_table = Table(scores_data, colWidths=[200, 100])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(Paragraph("Scores Summary", styles['Heading2']))
    elements.append(Spacer(1, 12))
    elements.append(scores_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_report_of_paper(output_model: PaperEvaluation) -> str:
    return " ".join([output_model.significance, output_model.methodology, 
                    output_model.presentation, output_model.justification,
                    output_model.major_strengths, output_model.major_weaknesses,
                    output_model.detailed_feedback])

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
# Page configuration
st.set_page_config(page_title="Paper Evaluation", page_icon="📜", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 2s ease-in-out;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main title
st.markdown('<div class="fade-in">Paper Evaluation System 📜</div>', unsafe_allow_html=True)
st.markdown("---")

# API Key handling in sidebar
st.sidebar.title("API Configuration")
groq_api_key = st.sidebar.text_input("Enter Groq API key:", type="password")
fallback_api_key = st.secrets.get('GROQ_API_KEY')

if not groq_api_key:
    if fallback_api_key:    
        groq_api_key = fallback_api_key
        st.sidebar.info("Using the fallback API Key.")
        st.sidebar.warning("This may cause rate limiting issues")
    else:
        st.sidebar.warning("Please enter your Groq API Key to proceed.")

# Initialize LLM and systems
llm = ModelManager.get_groq_llm(model_name="llama-3.1-8b-instant", api_key=groq_api_key)

classification_system = SystemClassification(
    llm=llm,
    debug=True
)

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
    debug=True
)

# Main upload section
st.write("Please upload a file size of less than 150 KB")
uploaded_file = st.file_uploader("Upload your research paper (PDF):", type="pdf")

with st.expander("Additional Options"):
    process_without_stop_words = st.checkbox("Process Without Stop Words")

if process_without_stop_words:
    st.warning("Processing without stop words might degrade the performance.")
    
classification_system.split_pdf_without_stop_words = process_without_stop_words

if uploaded_file:
    if uploaded_file.size > 150 * 1024:  
        st.warning("File size exceeds the limit of 150 KB. This may take up to 50 minutes to process")
    
    if st.button("Process Paper"):
        with st.spinner("Processing your paper. This may take 20-55 minutes. Please don't close the browser window."):
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
                
                
                # Process paper
                output_model = classification_system.classify_paper(path_to_pdf=temp_file_path)
                
                if output_model:
                    # Create report summary
                    report_summary = create_report_of_paper(output_model)
                    
                    st.header("Evaluation Results")
                    
                    # Download buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        pdf_buffer = generate_pdf(output_model)
                        st.download_button("Download PDF", pdf_buffer, "evaluation_report.pdf", "application/pdf")
                    with col2:
                        st.download_button("Download JSON", output_model.model_dump_json(indent=2), "evaluation_report.json")
                    with col3:
                        df = pd.DataFrame([output_model.model_dump()]).transpose()
                        df.columns = ['Value']
                        st.download_button("Download CSV", df.to_csv(), "evaluation_report.csv")
                    
                    # Display evaluation details
                    st.subheader("Research Significance")
                    st.write(output_model.significance)
                    
                    st.subheader("Methodology Assessment")
                    st.write(output_model.methodology)
                    
                    st.subheader("Presentation Quality")
                    st.write(output_model.presentation)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence Score", output_model.confidence_score)
                    with col2:
                        st.metric("Paper Score", output_model.score)
                    
                    st.subheader("Major Strengths")
                    st.write(output_model.major_strengths)
                    
                    st.subheader("Major Weaknesses")
                    st.write(output_model.major_weaknesses)
                    
                    st.subheader("Score Justification")
                    st.write(output_model.justification)
                    
                    st.subheader("Detailed Feedback")
                    st.write(output_model.detailed_feedback)
                    
                    st.subheader("Publication Recommendation")
                    st.write("✅ Publishable" if output_model.publishable else "❌ Not Publishable")
                    
                    # Save initial evaluation
                    if not output_model.publishable:
                         save_evaluation(
                            temp_file_path, False, output_model.justification, output_model.significance, 
                            output_model.methodology, output_model.presentation, output_model.confidence_score, 
                            output_model.score, output_model.major_strengths, output_model.major_weaknesses, 
                            output_model.detailed_feedback, 0, "", ""
                        )
                    
                    # Process conference recommendation if publishable
                    if output_model.publishable:
                        st.markdown("---")
                        st.title("Conference Recommendation")
                        
                        with st.spinner("Evaluating the best conference. Please wait..."):
                            conference_decision = conference_system.discuss_and_decide(report_of_paper=report_summary)
                            
                            if conference_decision:
                                save_evaluation(
                                    temp_file_path, True, output_model.justification, output_model.significance, 
                                    output_model.methodology, output_model.presentation, output_model.confidence_score, 
                                    output_model.score, output_model.major_strengths, output_model.major_weaknesses, 
                                    output_model.detailed_feedback, conference_decision["score"], 
                                    conference_decision["justification"], conference_decision["conference"]
                                )
                                
                                st.header("Recommended Conference")
                                st.subheader("Conference")
                                st.write(conference_decision["conference"])
                                st.subheader("Confidence Score")
                                st.write(conference_decision["score"])
                                st.subheader("Justification")
                                st.write(conference_decision["justification"])

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Made with ❤️ by Team HACKTIVATE</div>", unsafe_allow_html=True)