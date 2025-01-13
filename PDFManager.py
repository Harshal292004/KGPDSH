import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punk_tab')
nltk.download('punkt')
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

from RichLogger import RichLogger

class PDFSplitter:
      """
      Class for Spliting PDF with or without stop words
      
      """
      def __init__(self,debug=False,chunk_size: int = 100,chunk_overlap: int = 0):
          self.logger=RichLogger()
          self.debug=debug
          self.recursive_text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
          self.stop_words = set(stopwords.words('english'))
          
      def split_pdf_without_stop_words(self, pdf_pages: List[Document]) -> List[Document]:

        if self.debug:    
          self.logger.info("Splitting PDF without stop words")
          
        try:
              
          for page in pdf_pages:
            tokens=word_tokenize(page.page_content.lower())
            filtered_tokens = [word for word in tokens if word not in self.stop_words]
            page.page_content = ' '.join(filtered_tokens)

          split_documents = self.recursive_text_splitter.split_documents(pdf_pages)
          
          if len(split_documents)>54:    
            split_documents = [doc for i, doc in enumerate(split_documents) if i % 2 == 0]
    
        
          return split_documents

        except Exception as e:
          if self.debug:        
            self.logger.error(f"Error splitting PDF: {e}")    
          raise e
        
      def split_pdf(self, pdf_pages: List[Document],odd_even=False) -> List[Document]:
        
        try:
          if self.debug:    
            self.logger.info("Split Pdf")
      
          splitter= self.recursive_text_splitter
          split_documents = splitter.split_documents(pdf_pages)
          
          if len(split_documents)> 54:  
            split_documents = [doc for i, doc in enumerate(split_documents) if i % 2 == 0]
            
          return split_documents
      
        except Exception as e:
          if self.debug:    
            self.logger.error(f"Error splitting PDF: {e}")
          raise e
        
    
class PDFHandler:
    """
    A class for loading pdf
    """
    
    def __init__(self,debug=False):
      
      self.debug=debug
      self.logger=RichLogger()
      
    def load_pdf(self, pdf_file_path: str) -> List[Document]:
        pdf_pages = []
        
        try:
            if self.debug:    
                self.logger.info(f"Loading PDF: {pdf_file_path}")
                
            loader = PyPDFLoader(pdf_file_path)
            pdf_pages = loader.load()
        
        except Exception as e:
          
            if self.debug:
              self.logger.error(f"Error loading PDF: {e}")
            raise e 
                  
        return pdf_pages


