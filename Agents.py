from Prompts import Prompts
from Utility import ConferenceModel, PaperEvaluation

class Agents:
    """
    Class for declaring agents 
    """
    def __init__(self):
        pass

    @staticmethod
    def gen_classification_agent(llm):
        """
        Agent for classifying paper as publishable or not 
        """
        gen_classification_agent=Prompts.gen_classification_prompt()| llm
        return gen_classification_agent

    @staticmethod
    def paper_evaluation_model_agent(llm):
        """
        Agent for  generating PaperEvaluation Model 
        """
        paper_evaluation_model_agent = Prompts.gen_paper_evaluation_output_model_prompt() | llm.with_structured_output(PaperEvaluation)
        return paper_evaluation_model_agent

    @staticmethod
    def summarize_aspect_agent(aspect:str,llm):
        """
        Agent for summarizing aspect like  `justification`  into points
        """
        summarize_aspect_agent=Prompts.gen_aspect_summary_prompt(aspect=aspect) | llm
        return summarize_aspect_agent
    
    @staticmethod
    def get_conference_agent(llm):
        """
        Agnet for deciding conference
        """
        conference_agent=Prompts.get_conference_prompt() | llm.with_structured_output(ConferenceModel)
        return conference_agent