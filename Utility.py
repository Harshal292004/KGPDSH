
from typing import Annotated
from pydantic import BaseModel, Field

from langchain_community.vectorstores import PathwayVectorClient
from langchain_groq import ChatGroq



class ModelManager:
    def __init__(self):
        """Initialize the ModelManager class."""
        
    @staticmethod
    def get_groq_llm(model_name: str = "llama-3.3-70b-versatile",api_key: str = ""):
        
        llm_instance = ChatGroq(
            model=model_name,
            api_key=api_key
        )
        return llm_instance

class PaperEvaluation(BaseModel):
    significance: Annotated[str, Field(description="Provide a detailed evaluation of the research significance, including its impact on the field and any novel contributions (4-5 sentences)")]
    methodology: Annotated[str, Field(description="Assess the methodology used in the research, discussing its appropriateness and rigor (4-5 sentences)")]
    presentation: Annotated[str, Field(description="Evaluate the quality of presentation, including clarity and organization of ideas (4-5 sentences)")]
    confidence_score: Annotated[float, Field(description="Rate your confidence in your evaluation on a scale from 1 to 10 (whole numbers only)")]
    score: Annotated[float, Field(description="Provide an score for the paper on a scale from 0 to 10")]
    major_strengths: Annotated[str, Field(description="List key strengths of the paper with specific examples")]
    major_weaknesses: Annotated[str, Field(description="List key weaknesses of the paper with specific examples")]
    justification: Annotated[str, Field(description="Provide a thorough justification for your scores and evaluations (at least 5 sentences)")]
    detailed_feedback: Annotated[str, Field(description="Offer comprehensive feedback and suggestions for improvement")]
    publishable: Annotated[bool, Field(description="Indicate whether you believe the paper is publishable based on your evaluation")]
     

class ConferenceModel(BaseModel):
    score: Annotated[float, Field(description="The evaluation score used to determine the suitability of the paper for the conference")]
    justification: Annotated[str, Field(description="A detailed explanation of the assigned score, including reasons for acceptance or rejection of the paper by the conference")]
    
    
class Utilities:
    """
    A class for utility functions and Pathyway client.
    """
    def __init__(self):
          pass

    @staticmethod
    def client_store(url="https://demo-document-indexing.pathway.stream"):
        client = PathwayVectorClient(url=url)
        return client

    @staticmethod
    def retrieve_conference_context(vector_store:PathwayVectorClient, query: str,query_about:str) -> str:
        results = vector_store.similarity_search(query=query, top_k=3)
        return "\n".join([result.page_content for result in results if query_about in result.page_content])


