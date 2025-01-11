from RichLogger import RichLogger
from Agents import Agents
import time

from typing import List
from Utility import  PaperEvaluation
from langchain_core.documents import Document
from PDFManager import PDFHandler,PDFSplitter

class SystemSTORM:
    def __init__(
      self,
      llm,
      cvpr_theme:str,
      cvpr_context:str,
      neur_ips_theme:str,
      neur_ips_context:str,
      emnlp_theme:str,
      emnlp_context:str,
      kdd_theme:str,
      kdd_context:str,
      tmlr_theme:str,
      tmlr_context:str,
      daa_theme:str,
      daa_context:str,
      wait_time:float=45.0,
      debug=False
    ):
          
          self.cvpr_agent=Agents.get_conference_agent(llm)
          self.neur_ips_agent=Agents.get_conference_agent(llm)
          self.emnlp_agent=Agents.get_conference_agent(llm)
          self.kdd_agent=Agents.get_conference_agent(llm)
          self.tmlr_agent=Agents.get_conference_agent(llm)
          self.daa_agent=Agents.get_conference_agent(llm)
          
          self.cvpr_theme=cvpr_theme
          self.cvpr_context=cvpr_context
          self.neur_ips_theme=neur_ips_theme
          self.neur_ips_context=neur_ips_context
          self.emnlp_theme=emnlp_theme
          self.emnlp_context=emnlp_context
          self.kdd_theme=kdd_theme
          self.kdd_context=kdd_context
          self.tmlr_theme=tmlr_theme
          self.tmlr_context=tmlr_context
          self.daa_theme=daa_theme
          self.daa_context=daa_context
          self.wait_time=wait_time
          
          self.logger=RichLogger()
          self.debug=debug

    def discuss_and_decide(self, report_of_paper: str) :
        discussions = []
        conference_array=[]
        
        discuss_cvpr=self.cvpr_agent.invoke({"target_conference":"CVPR","conference_theme":self.cvpr_theme,"conference_context":self.cvpr_context,"report_of_paper":report_of_paper})
        discussions.append(discuss_cvpr)
        conference_array.append("CVPR")
        time.sleep(self.wait_time)
        
        discuss_neur_ips=self.neur_ips_agent.invoke({"target_conference":"NeurIPS","conference_theme":self.neur_ips_theme,"conference_context":self.neur_ips_context,"report_of_paper":report_of_paper, })
        discussions.append(discuss_neur_ips)
        conference_array.append("NeurIPS")
        time.sleep(self.wait_time)
        
        discuss_emnlp=self.emnlp_agent.invoke({"target_conference":"EMNLP","conference_theme":self.emnlp_theme,"conference_context":self.emnlp_context,"report_of_paper":report_of_paper, })
        discussions.append(discuss_emnlp)
        conference_array.append("EMNLP")
        time.sleep(self.wait_time)
        
        discuss_kdd=self.kdd_agent.invoke({"target_conference":"KDD","conference_theme":self.kdd_theme,"conference_context":self.kdd_context,"report_of_paper":report_of_paper, })
        discussions.append(discuss_kdd)
        conference_array.append("KDD")
        time.sleep(self.wait_time)
        
        discuss_tmlr=self.tmlr_agent.invoke({"target_conference":"TMLR","conference_theme":self.tmlr_theme,"conference_context":self.tmlr_context,"report_of_paper":report_of_paper, })
        discussions.append(discuss_tmlr)
        conference_array.append("TMLR")
        time.sleep(self.wait_time)
        
        discuss_daa=self.daa_agent.invoke({"target_conference":"DAA","conference_theme":self.daa_theme,"conference_context":self.daa_context,"report_of_paper":report_of_paper, })
        discussions.append(discuss_daa)
        conference_array.append("DAA")

        best_conference= discussions[0]
        score= best_conference.score
        target_conference="CVPR"
        
        for index,discussion in enumerate(discussions):
            if self.debug:
                self.logger.debug(f"{discussion.score} {conference_array[index]}")
            if discussion.score is not None and discussion.score > best_conference.score:
                best_conference = discussion
                target_conference=conference_array[index]
                score=best_conference.score
        
        return {
           "conference":target_conference ,
           "score":score ,
           "justification": best_conference.justification
        }



class SystemClassification:
    def __init__(self,
          llm,
          debug: bool = False,
          wait_time: float = 15.0,
          wait_time_per_chunk: float = 5.0,
          wait_time_for_summary: float = 45.0,
          wait_time_per_five_chunk: float = 5.0,
          wait_time_per_five_chunk_model: float = 10.0,
          wait_time_after_model: float = 3.0,
          wait_time_recurrsion: float = 2,
          
          split_without_stop_words:bool=False,
          odd_even:bool=False,
          threshold: int = 16000):
          
        self.pdf_handler=PDFHandler()
        self.pdf_splitter=PDFSplitter(chunk_size=1024,chunk_overlap=256)
        
        self.classification_agent = Agents.gen_classification_agent(llm)
        self.paper_evaluation_model_agent = Agents.paper_evaluation_model_agent(llm)
       
        array_of_aspects = ["significance", "methodology", "presentation", "justification", "major strengths", "major weaknesses", "detailed feedback"]
        self.aspect_agents=[]

        for aspect in array_of_aspects:
          self.aspect_agents.append(Agents.summarize_aspect_agent(aspect=aspect,llm=llm))
          
        self.debug = debug
        
        self.wait_time_per_chunk = wait_time_per_chunk
        self.wait_time_per_five_chunk = wait_time_per_five_chunk
        self.wait_time_after_model = wait_time_after_model
        self.wait_time_for_summary = wait_time_for_summary
        self.wait_time_recurrsion = wait_time_recurrsion
        self.wait_time = wait_time
        self.wait_time_per_five_chunk_model = wait_time_per_five_chunk_model
        self.threshold = threshold
        
        self.split_without_stop_words=split_without_stop_words
        self.odd_even=odd_even
        self.llm=llm 
        self.logger=RichLogger()
        
        
    def log_and_wait(self, message: str, wait_time: float):
        if self.debug:
            self.logger.debug(f"{message} Waiting for {wait_time} seconds.")
        time.sleep(wait_time)
        if self.debug:
            self.logger.debug("Resumed execution.")

    def convert_to_paper_evaluation_model(self, analyzed_chunks_list: List[str]):
      
      paper_evaluation_list = []
      
      if self.debug:
        self.logger.info("Starting conversion to paper evaluation model.")

      for index, chunk in enumerate(analyzed_chunks_list):
          try:
              if self.debug and index % 5 == 0:
                self.logger.info(f"Converting chunk {index + 1}/{len(analyzed_chunks_list)}")

              if index % 5 == 0 :
                self.log_and_wait("Sleeping before processing the next set of chunks", self.wait_time_per_five_chunk_model)

              paper_evaluation_model = self.paper_evaluation_model_agent.invoke({"classification_string": chunk})

              if self.debug:
                self.logger.info("Waiting after processing a model.")
              self.log_and_wait("Sleeping after processing a model", self.wait_time_after_model)

              paper_evaluation_list.append(paper_evaluation_model)
          except Exception as e:
              if self.debug:
                self.logger.error(f"Error processing chunk {index + 1}")
              raise e

      if self.debug:
        self.logger.success("Conversion to paper evaluation model completed.")

      return paper_evaluation_list

    def derive_final_output(self, paper_evaluation_model_list: List[PaperEvaluation]):    
      if self.debug:
        self.logger.info("Starting derivation of the final output.")

      try:
        total_chunks = len(paper_evaluation_model_list)
        publishable_result = 0
        non_publishable_result = 0
        final_publishable_result = False
        final_average_score = 0
        final_average_confidence = 0

        for i, model in enumerate(paper_evaluation_model_list):
          if self.debug:
            self.logger.info(f"Processing chunk {i + 1}/{total_chunks}")
            self.logger.debug(f"Score: {model.score}, Confidence: {model.confidence_score}")

          final_average_score += model.score
          final_average_confidence += model.confidence_score

          if model.publishable:
              publishable_result += 1

          else:
              non_publishable_result += 1

        if publishable_result > non_publishable_result:
            final_publishable_result = True

        final_average_score /= total_chunks
        final_average_confidence /= total_chunks

        final_paper_evaluation = PaperEvaluation(
            significance=" ".join(model.significance for model in paper_evaluation_model_list),
            methodology=" ".join(model.methodology for model in paper_evaluation_model_list),
            presentation=" ".join(model.presentation for model in paper_evaluation_model_list),
            confidence_score=final_average_confidence,
            score=final_average_score,
            major_strengths=" ".join(model.major_strengths for model in paper_evaluation_model_list),
            major_weaknesses=" ".join(model.major_weaknesses for model in paper_evaluation_model_list),
            justification=" ".join(model.justification for model in paper_evaluation_model_list),
            detailed_feedback=" ".join(model.detailed_feedback for model in paper_evaluation_model_list),
            publishable=final_publishable_result
        )

        if self.debug:
          self.logger.success("Final output derived successfully.")

        return final_paper_evaluation
      except Exception as e:
        if self.debug:
          self.logger.error(f"Error deriving final output: {e}")
        raise e


    def get_model(self, aspect: str = "justification"):

      models={
        "justification":self.aspect_agents[3],
        "methodology":self.aspect_agents[1],
        "presentation":self.aspect_agents[2],
        "significance":self.aspect_agents[0],
        "major strengths":self.aspect_agents[4],
        "major weaknesses":self.aspect_agents[5],
      }

      return models.get(aspect, self.aspect_agents[6])

    def merge_and_summarize_aspect(self, aspect_str: str, left: int, right: int, aspect: str = "justification"):
      if self.debug:
        self.logger.info(f"Merging and summarizing aspect: {aspect}")
      length_of_string = right - left

      if length_of_string <= self.threshold:
          model = self.get_model(aspect=aspect)
          chunk = aspect_str[left:right]
          try:
              if self.debug:
                  self.logger.info(f"Invoking model for chunk with length {length_of_string}.")

              summary = model.invoke({"aspect_string": chunk})
              if self.debug:
                  self.log_and_wait(message="Merge and summarize",wait_time=self.wait_time_recurrsion)
              return str(summary.content)
          except Exception as e:
              if self.debug:
                self.logger.error(f"Error invoking model: {e}")
              return ""

      mid = (left + right) // 2
      left_summary = self.merge_and_summarize_aspect(aspect_str, left, mid, aspect)
      right_summary = self.merge_and_summarize_aspect(aspect_str, mid + 1, right, aspect)
      combined_summary = left_summary + " " + right_summary

      if len(combined_summary) > self.threshold:
          model = self.get_model(aspect=aspect)
          try:
              if self.debug:
               self.logger.info(f"Re-summarizing combined summary exceeding threshold.")
              combined_summary = model.invoke({"aspect_str": combined_summary[:self.threshold]})
              if self.debug:
                self.log_and_wait(message="Merge and summarize",wait_time=self.wait_time_recurrsion)
              return str(combined_summary.content)
          except Exception as e:
              if self.debug:
                self.logger.error(f"Error during re-summarization: {e}")
              return ""

      return combined_summary

    def summarize_final_output_model(self, final_output_model:PaperEvaluation):
      if self.debug:
        self.logger.info("Starting summarization of the final output.")

      justification = self.merge_and_summarize_aspect(final_output_model.justification,0,len(final_output_model.justification),aspect="justification")
      self.log_and_wait(message="After summary",wait_time=self.wait_time_for_summary)
      methodology = self.merge_and_summarize_aspect(final_output_model.methodology,0,len(final_output_model.methodology),aspect="methodology")
      self.log_and_wait(message="After summary",wait_time=self.wait_time_for_summary)
      presentation = self.merge_and_summarize_aspect(final_output_model.presentation,0,len(final_output_model.presentation),aspect="presentation")
      self.log_and_wait(message="After summary",wait_time=self.wait_time_for_summary)
      significance = self.merge_and_summarize_aspect(final_output_model.significance,0,len(final_output_model.significance),aspect="significance")
      self.log_and_wait(message="After summary",wait_time=self.wait_time_for_summary)
      major_strengths = self.merge_and_summarize_aspect(final_output_model.major_strengths,0,len(final_output_model.major_strengths),aspect="major strengths")
      self.log_and_wait(message="After summary",wait_time=self.wait_time_for_summary)
      major_weaknesses = self.merge_and_summarize_aspect(final_output_model.major_weaknesses,0,len(final_output_model.major_weaknesses),aspect="major weaknesses")
      self.log_and_wait(message="After summary",wait_time=self.wait_time_for_summary)
      detailed_feedback = self.merge_and_summarize_aspect(final_output_model.detailed_feedback,0,len(final_output_model.detailed_feedback),aspect="detailed feedback")

      if self.debug:
        self.logger.success("Final output summarized successfully.")

      return justification,methodology,presentation,significance, major_strengths,major_weaknesses,detailed_feedback

    def analyze_chunk(self, pdf_chunk_str: str) -> str:

        if self.debug:
          self.logger.info(f"Analyzing chunk of size {len(pdf_chunk_str)} characters.")

        try:

            classification = self.classification_agent.invoke({"chunk_of_paper": pdf_chunk_str})
            classification_str = str(classification.content)

            if self.debug:
              self.logger.info(message=f"Classification: {classification_str[:50]}...")


            self.log_and_wait(message="After classification",wait_time=self.wait_time_per_chunk)

            return classification_str

        except Exception as e:
            if self.debug:
              self.logger.error(f"Error analyzing chunk: {e}")
            raise e


    def analyze_page_chunks(self, splitted_pdf: List[Document]):

        paper_evaluation_list = []
        total_chunks = len(splitted_pdf)
        if self.debug:    
          self.logger.info(f"Starting analysis of {total_chunks} chunks.")

        for index, chunk in enumerate(splitted_pdf):

            try:
                if self.debug and index % 5 == 0:
                    self.logger.info(f"{chunk.page_content} ...")
                    self.logger.info(f"Processing chunk {index + 1}/{total_chunks}")

                if index % 5==0:
                  self.log_and_wait(message="Sleeping before processing the next set of chunks",wait_time=self.wait_time_per_five_chunk)

                paper_evaluation_list.append(self.analyze_chunk(pdf_chunk_str=chunk.page_content))

            except Exception as e:

              if self.debug:
                self.logger.error(f"Error processing chunk {index + 1}")

              raise e

        if self.debug:
          self.logger.success("Chunk analysis completed.")

        return paper_evaluation_list


    def classify_paper(self,path_to_pdf:str):

        if self.debug:
            self.logger.info(f"Classifying paper: {path_to_pdf}")

        try:
            page_loaded=self.pdf_handler.load_pdf(pdf_file_path=path_to_pdf)
            # analysis of page chunks
            
            splitted_pdf = (
              self.pdf_splitter.split_pdf(page_loaded,odd_even=self.odd_even)
              if not self.split_without_stop_words
              else self.pdf_splitter.split_pdf_without_stop_words(page_loaded,odd_even=self.odd_even)
            )

            paper_evaluation_list = self.analyze_page_chunks(splitted_pdf)
            

            self.log_and_wait(message="Sleep after paper evaluation",wait_time=self.wait_time)
            # models in page evaluation
            paper_evaluation_model_list = self.convert_to_paper_evaluation_model(paper_evaluation_list)


            # this will take no time just a loop
            final_paper_evaluation_model = self.derive_final_output(paper_evaluation_model_list)

            self.log_and_wait(message="Sleep after before summarization",wait_time=self.wait_time)

            # summarize everthing here is where fat rahi hai
            justification,methdology,presentation,significance, major_strengths,major_weaknesses,detailed_feedback=self.summarize_final_output_model(final_output_model=final_paper_evaluation_model)

            # Intilaize the final model
            final_output_model = PaperEvaluation(
              significance=significance,
              methodology=methdology,
              presentation=presentation,
              confidence_score=final_paper_evaluation_model.confidence_score,
              score=final_paper_evaluation_model.score,
              major_strengths=major_strengths,
              major_weaknesses=major_weaknesses,
              justification=justification,
              detailed_feedback=detailed_feedback,
              publishable=final_paper_evaluation_model.publishable
            )

            if self.debug:
              self.logger.info(f"Paper classification completed successfully.")

            return final_output_model
        except Exception as e:
            self.logger.error("Error classifying paper: %s")
            raise e