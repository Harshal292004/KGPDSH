from langchain_core.prompts import ChatPromptTemplate

class Prompts:
    """Class for generating prompts for analysis."""

    @staticmethod
    def gen_classification_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You will classify the paper based on its publishability as true or false.

                    Tasks:
                    - Assess the paper's significance, methodology, and presentation quality in detail with about 2-3 sentences.
                    - Assign a score (0-10) with a confidence score (1-10) for your evaluation.
                    - Note: Confidence should be a whole number (e.g., 1, 2, ..., 10), not decimal values like 0.5 or 0.9.
                    - Provide a detailed justification for your score.
                    - Identify major strengths and weaknesses of the paper with specific examples.
                    - Suggest improvements if applicable; otherwise, state "No improvement needed."

                    Your output must strictly conform to the following JSON schema without any additional text or comments:
                    Output Schema:
                      "significance":string,"Provide a detailed evaluation of the research significance, including its impact on the field and any novel contributions (4-5 sentences).",
                      "methodology":string,"Assess the methodology used in the research, discussing its appropriateness and rigor (2-3 sentences).",
                      "presentation":string, "Evaluate the quality of presentation, including clarity and organization of ideas (2-3 sentences)",
                      "confidence_score":int, Rate your confidence in your evaluation on a scale from 1 to 10 (whole numbers only),
                      "score":float, Provide an score for the paper on a scale from 0 to 10,
                      "major_strengths":string, "List key strengths of the paper with specific examples",
                      "major_weaknesses":string, "List key wekness of the paper with specific examples",
                      "justification":string, "Provide a thorough justification for your scores and evaluations (at most 4 sentences)",
                      "detailed_feedback":string,"Offer comprehensive feedback and suggestions for improvement",
                      "publishable": bool
                    """
                ),
                (
                    "human",
                    """
                    {chunk_of_paper}
                    """
                )
            ]
        )

    @staticmethod
    def gen_paper_evaluation_output_model_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You will receive an analysis string containing:
                - significance
                - methodology
                - presentation
                - confidence_score
                - score
                - major_strengths
                - major_weaknesses
                - justification
                - detailed_feedback
                - publishable

                **Important:** There may be additional commentary in the analysis string. Strictly ignore any such commentary.

                Your task is to structure the output in a structured format WITHOUT CHANGING ANYTHING.
                """
            ),
            (
                "human",
                """
                {classification_string}
                """
            )
        ])

    @staticmethod
    def gen_aspect_summary_prompt(aspect) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    Summarize the {aspect} string into a polished final 5 detailed points.
                    Ensure logical flow within the {aspect}.

                    Your output should contain only the summary, with no additional commentary like 'Here are the 15 detailed points of feedback'.
                    """
                ),
                (
                    "human",
                    """
                    {aspect_string}
                    """
                )
            ]
        )
        
    @staticmethod
    def get_conference_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are the representative for the conference {target_conference}.
                Theme: {conference_theme}
                Context: {conference_context}

                Key Differences Between Conferences:

                1. Focus Area and Scope:
                  - CVPR: Specialized in computer vision and visual computing
                  - NeurIPS: Broad coverage of machine learning and computational neuroscience
                  - EMNLP: Focused on natural language processing and computational linguistics
                  - KDD: Centered on data mining and practical applications
                  - TMLR: Emphasizes theoretical machine learning research
                  - DAA: Concentrates on enterprise data architecture and analytics

                2. Research Style:
                  - CVPR: Strong emphasis on empirical results and practical applications
                  - NeurIPS: Balance of theoretical and applied research, with focus on novelty
                  - EMNLP: Emphasis on empirical methods and linguistic foundations
                  - KDD: Focus on practical, scalable solutions for real-world problems
                  - TMLR: Prioritizes theoretical depth and mathematical rigor
                  - DAA: Focuses on implementation and enterprise architecture

                3. Industry vs. Academic Focus:
                  - CVPR: Strong industry presence, especially from tech and automotive sectors
                  - NeurIPS: Mixed academic and industry participation
                  - EMNLP: Primarily academic with growing industry interest
                  - KDD: Strong industry focus with practical applications
                  - TMLR: Primarily academic with theoretical focus
                  - DAA: Heavily industry-focused with enterprise emphasis

                4. Evaluation Emphasis:
                  - CVPR: Performance metrics and real-world applicability
                  - NeurIPS: Theoretical novelty and experimental rigor
                  - EMNLP: Linguistic validity and empirical results
                  - KDD: Scalability and practical impact
                  - TMLR: Mathematical rigor and theoretical foundations
                  - DAA: Implementation feasibility and business value

                5. Impact Areas:
                  - CVPR: Robotics, autonomous systems, medical imaging
                  - NeurIPS: General AI advancement, cognitive science
                  - EMNLP: Language technologies, digital humanities
                  - KDD: Business intelligence, social network analysis
                  - TMLR: Foundational ML research, algorithm development
                  - DAA: Enterprise systems, data infrastructure

                Be very Brutual and honest
                Evaluate the report of a research paper and determine whether it's suitable for your conference.
                Score it (0-10) and justify why it fits or doesn't for the conference .
                Output must follow this JSON schema:
                - score: float
                - justification: str
                """
            ),
            (
                "human",
                """
                Report of paper: {report_of_paper}
                """
            )
        ])