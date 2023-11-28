import yaml

from typing import List, Dict, Optional

from omegaconf import OmegaConf
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from pydantic import BaseModel


######################## GLOBAL CONFIGURATION ########################
CONFIG = OmegaConf.create(
    yaml.load(
        open("config/model.yaml"),
        Loader=yaml.FullLoader
    )
)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

template = """### Human: {question}

### Agent: Let's work this out in a step by step way to be sure we have the right answer.
### Response: {answer}"""

prompt = PromptTemplate(template=template, input_variables=["question"])

############################ DEFINITIONS ############################
class ChatBot:

    def __init__(self):
        self._chain = self.create_chain()


    def _load_model(self):
        global CONFIG
        global callback_manager
        config = CONFIG.llm
        return LlamaCpp(
            callback_manager=callback_manager,
            **config.runtime_args
        )

    def _load_vectorstore(self):
        global CONFIG
        config = CONFIG.vectorstore
        loader = DirectoryLoader('/data', glob="**/*.md")
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            **config.text_splitter
        )
        all_splits = text_splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(**config.vectorstore.model)
        
        return FAISS.from_documents(all_splits, embeddings)

    def create_chain(self):
        llm = self._load_model()
        vectorstore = self._load_vectorstore()
        chain = ConversationalRetrievalChain.from_llm(
            llm,
            vectorstore.as_retriever(),
            return_source_documents=True
        )
        return chain

    def reply(self, prompt: str, chat_history: Optional[List[Dict]]=None):
        result = self._chain(
            {
                "question": prompt,
                "chat_history": chat_history
            }
        )
        return {
            "answer": result["answer"],
            "source_documents": [
                x.get("metadata") for x 
                in result["source_documents"]
            ]
        }

    
########################### DATA STRUCTURES ###########################
class Input(BaseModel):
    prompt: str
    chat_history: Optional[List[Dict]] = None 

class Output(BaseModel):
    answer: str
    source_documents: List[Dict] = None
