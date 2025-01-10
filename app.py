import streamlit as st
import time
from langchain.prompts.chat import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import os
import tempfile
from pymongo import MongoClient

# Streamlit UI
st.set_page_config(page_title="Paper Evaluation", page_icon="📜", layout="wide")

st.sidebar.title("Navigation")
groq_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not groq_api_key:
    st.sidebar.warning("Please enter your Groq API Key to proceed.")
    st.stop()

# MongoDB connection
MONGO_URI = st.secrets["MONGO_URI"]  # Store the URI securely in Streamlit Secrets
client = MongoClient(MONGO_URI)
db = client["paper_evaluations"]  # Replace with your database name
collection = db["paper_evaluations"]  # Replace with your collection name

def save_evaluation(paper_id, publishable, justification, conference_rationale):
    document = {
        "paper_id": paper_id,
        "publishable": publishable,
        "justification": justification,
        "conference_rationale": conference_rationale
    }
    collection.insert_one(document)
    st.success("Evaluation saved successfully!")

# Initialize LangChain components
chat_model = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key)

class PublishabilityEvaluator:
    def __init__(self, chat_model: ChatGroq, publishable_retriever, not_publishable_retriever, example_publishable, example_not_publishable):
        """
        Initialize the evaluator with LLM and retrievers for publishable and not-publishable examples.
        """
        self.chat_model = chat_model
        self.publishable_retriever = publishable_retriever
        self.not_publishable_retriever = not_publishable_retriever
        self.example_publishable = example_publishable
        self.example_not_publishable = example_not_publishable

    def evaluate_publishability(self, paper_text: str) -> dict:
        """
        Evaluate the publishability of a research paper using chunking and example-based classification.
        """
        # Prepare the examples
        prompt = f"""
        You will be given a research paper, and your task is to classify it as "Publishable" or "Not Publishable".
        For reference, I have provided two examples:

        1. Publishable Paper:
        {self.example_publishable}

        2. Not Publishable Paper:
        {self.example_not_publishable}

        Criteria for classification:
        - Methodology clarity: Is the methodology well-defined and replicable?
        - Coherence: Does the paper follow a logical structure?
        - Validity: Are the results justified with evidence?

        Now, analyze the following research paper and provide your classification along with a brief justification.
        """

        # Chunk the input paper
        chunks = self.chunk_text(paper_text)
        chunk_results = []  # To collect classification and justification per chunk

        for chunk in chunks:
            context = f"{prompt}\n\nResearch Paper:\n{chunk}"
            try:
                response = self.chat_model.invoke(context)
                print("Response:", response)

                # Extract classification and justification
                classification = "Publishable" if "Classification: Publishable" in response.content else "Not Publishable"
                justification = response.content  # Assuming full content includes justification

                chunk_results.append({
                    "chunk_text": chunk,
                    "classification": classification,
                    "justification": justification,
                })
            except Exception as e:
                print(f"Error processing chunk: {e}")

        return {
            "chunk_results": chunk_results,
        }

    def summarize_in_batches(self, chunk_results: list, batch_size: int = 5) -> dict:
        """
        Summarize chunk results in batches to handle context length limits.
        """
        summaries = []
        for i in range(0, len(chunk_results), batch_size):
            batch = chunk_results[i:i + batch_size]
            batch_prompt = f"""
            You are analyzing a batch of research paper evaluations. Each chunk has been classified as
            "Publishable" or "Not Publishable" with a justification. Summarize the justifications for this batch
            and provide a batch-level conclusion.
    
            Batch Evaluations:
            {json.dumps(batch, indent=2)}

            Respond with:
            - Batch Summary: A summary of the justifications for this batch.
            - Publishable Count: The number of chunks classified as Publishable in this batch.
            - Not Publishable Count: The number of chunks classified as Not Publishable in this batch.
            """

            response = self.chat_model.invoke(batch_prompt)
            try:
                result = json.loads(response.content)
                summaries.append(result)
            except json.JSONDecodeError:
                summaries.append({"batch_summary": response.content, "publishable_count": 0, "not_publishable_count": 0})

        # Combine all summaries into a final prompt
        combined_prompt = f"""
        You have received summaries of multiple batches of research paper evaluations. Combine these summaries into
        a final 500-word summary. Also calculate the total Publishable and Not Publishable counts across all batches
        and determine the final classification.

        Batch Summaries:
        {json.dumps(summaries, indent=2)}

        Respond with:
        - Final Summary: A 500-word summary combining all batch summaries.
        - Total Publishable Count: The total number of Publishable classifications.
        - Total Not Publishable Count: The total number of Not Publishable classifications.
        - Final Classification: "Publishable" or "Not Publishable" based on the higher count.
        """
        response = self.chat_model.invoke(combined_prompt)
        print(response)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"final_summary": response.content, "final_classification": "Error"}


    @staticmethod
    def chunk_text(text, max_chunk_size=1500):
        """
        Split text into manageable chunks for processing.
        """
        return [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]


# Loading and Chunking the Paper
    def load_and_chunk_paper(file_path: str, chunk_size: int = 500, overlap: int = 50) -> str:
            """Load a research paper and split it into manageable chunks."""
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            full_text = " ".join([page.page_content for page in pages])
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
            chunks = splitter.split_text(full_text)
            return " ".join(chunks)  # Combine chunks for processing

    def recursively_get_pdf_files(directory):
        pdf_files = []
        try:
            if os.path.isfile(directory) and directory.endswith('.pdf'):
                pdf_files.append(directory)
            elif os.path.isdir(directory):
                for file in os.listdir(directory):
                    full_path = os.path.join(directory, file)
                    pdf_files.extend(PublishabilityEvaluator.recursively_get_pdf_files(full_path))
        except Exception as e:
            print(f"Error accessing {directory}: {e}")
        return pdf_files

    def load_docs(list_of_pdf_paths):
        document_list=[]
        for pdf_path in list_of_pdf_paths:
          loader = PyPDFLoader(pdf_path)
          document_list.append(loader.load())
        return document_list

class ConferenceAgent:
    def __init__(self, name, chat_model, target_conference, conference_themes, conference_context):
        self.name = name
        self.chat_model = chat_model
        self.target_conference = target_conference
        self.conference_themes = conference_themes
        self.conference_context = conference_context

    def evaluate_paper(self, paper_summary):
        prompt = ChatPromptTemplate.from_template(
            """
            You are a representative of {target_conference}. Evaluate the paper for relevance, methodology, and novelty based on the following themes:
            {themes}

            Paper Summary:
            {summary}

            Provide a score (0-10) and a justification for your decision in JSON format.
            """
        )
        response = self.chat_model.generate(
            prompt.format_prompt(
                target_conference=self.target_conference,
                themes=self.conference_themes,
                summary=paper_summary
            ).to_messages()
        )
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response: {response.content}") from e

class STORMSystem:
    def __init__(self, agents):
        self.agents = agents

    def discuss_and_decide(self, paper_summary):
        evaluations = []
        for agent in self.agents:
            evaluation = agent.evaluate_paper(paper_summary)
            evaluations.append({
                "conference": agent.target_conference,
                "score": evaluation["score"],
                "justification": evaluation["justification"],
            })

        best_conference = max(evaluations, key=lambda x: x["score"])
        return {
            "best_conference": best_conference["conference"],
            "justification": best_conference["justification"],
        }

# CSS for Animations
st.markdown(
    """
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 2s ease-in-out;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #4CAF50;
    }

    .slide-up {
        animation: slideUp 1.5s ease-in-out;
        margin-top: 20px;
        text-align: center;
    }

    .button {
        animation: fadeIn 1.5s ease-in;
        display: inline-block;
        padding: 10px 20px;
        font-size: 1.2rem;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .button:hover {
        background-color: #45a049;
    }

    .footer {
        animation: slideUp 1.5s ease-in-out;
        margin-top: 50px;
        text-align: center;
        color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation

options = st.sidebar.radio("Choose an action:", ["Home", "Evaluate Publishability", "Determine Best Conference"])

if options == "Home":
    st.markdown('<div class="fade-in">Welcome to the Paper Evaluation System! 📜</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="slide-up">This system evaluates research papers for publishability and determines the best conference for publishing.</div>""",
        unsafe_allow_html=True
    )

elif options == "Evaluate Publishability":
    st.success("Please provide a file size of less than 100 KB")
    st.title("Tumhare baap ka LLM nahi hai ki 100 KB ke upar ki file daloge")
    st.title("📋 Publishability Evaluation")
    uploaded_file = st.file_uploader("Upload your research paper (PDF):", type="pdf", help="Limit 100 kb per file", )

    with st.expander("Additional Options"):
        strictness_level = st.radio("Select Strictness Level for Evaluation:", ["Easy", "Medium", "Normal", "Brutal"], index=1)

    if uploaded_file:
        st.info("Processing your file. Please wait...")

        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        # Extract text from PDF
        loader = PyPDFLoader(temp_file_path)
        paper_text = " ".join([page.page_content for page in loader.load()])

        # Evaluate publishability
        evaluator = PublishabilityEvaluator(chat_model)
        evaluation = evaluator.evaluate_publishability(paper_text)

        publishable = evaluation['chunk_results'][0]['classification'] == "Publishable"
        justification = evaluation['chunk_results'][0]['justification']

        save_evaluation(publishable, justification)

        st.markdown("### Publishability Result")
        st.write(f"**Publishable:** {evaluation['publishable']}")
        st.write(f"**Methodology Score:** {evaluation['methodology_score']}")
        st.write(f"**Coherence Score:** {evaluation['coherence_score']}")
        st.write(f"**Validity Score:** {evaluation['validity_score']}")
        st.write(f"**Justification:** {evaluation['justification']}\n")

    
        if evaluation['publishable']:
            st.session_state["publishable"] = True
            st.session_state["paper_summary"] = evaluation["summary"]
        else:
            st.session_state["publishable"] = False

elif options == "Determine Best Conference":
    st.title("🌟 Best Conference Determination")

    if st.session_state.get("publishable"):
        summary = st.session_state.get("paper_summary", "")
        st.markdown("### Paper Summary")
        st.text_area("Summary:", value=summary, height=200, disabled=True)

        if st.button("Determine Best Conference", key="determine"):
            st.info("Evaluating the best conference. Please wait...")

            agents = [
                ConferenceAgent(
                    name="Agent CVPR",
                    chat_model=chat_model,
                    target_conference="CVPR",
                    conference_themes="Computer Vision, Pattern Recognition",
                    conference_context="Focus on image processing and deep learning."
                ),
                ConferenceAgent(
                    name="Agent NeurIPS",
                    chat_model=chat_model,
                    target_conference="NeurIPS",
                    conference_themes="Machine Learning, AI, Neural Networks",
                    conference_context="Focus on theoretical and applied ML research."
                )
            ]

            storm = STORMSystem(agents)
            decision = storm.discuss_and_decide(summary)

            st.markdown(f'<div class="slide-up">The best conference for this paper is: <b>{decision["best_conference"]}</b></div>', unsafe_allow_html=True)
            st.markdown(f"<div class='slide-up'><b>Justification:</b> {decision['justification']}</div>", unsafe_allow_html=True)
    else:
        st.warning("Please evaluate the paper's publishability first.")

# Footer
st.markdown(
    """<div class="footer">Made with ❤️ for Research Evaluation</div>""",
    unsafe_allow_html=True
)

