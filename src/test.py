import os
from dotenv import load_dotenv
from langchain.llms.openai import OpenAI
from langchain import PromptTemplate, LLMChain
from langchain.callbacks import get_openai_callback
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from  document_handler import DocumentHandler

#some important enviroment variables
load_dotenv()
GRAMMAR_PATH = os.getenv("GRAMMAR_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")

#https://python.langchain.com/docs/modules/model_io/models/llms/token_usage_tracking

class LLM:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.model = None
        self.llm_chain = None
        self.prompts = {0: {"template": """Identify which dependencies the file uses and do a brief explanation of what the file contains.
                                 You must return a json with this fields:

                                 "dependencies": [list of dependencies names, external libraries as 'ext#library' and internal
                                 libraries as 'int#library' are accepted, for example: 'ext#numpy', 'int#my_library.plotter', 
                                 include imports like 'from lib import something',
                                 if 'from lib import something' write it as '(int or ext)#lib', 
                                 if 'from lib.sublib import something' write it as '(int or ext)#lib.sublib' and so on],
                                 "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                 and methods.'""

                                 give me the json ONLY, File received: {code}""", 
                            "input_variables": ["code"], 
                            "prompt_token_lenght": 267
                            }
                        }
        self.load_model()
        self.add_template_token_lenght()

    def add_template_token_lenght(self) -> None:
        """
            Adds the prompt token lenght field to each template. 
            this is used to know how small should be the context window for each template, 
            given that some space is already used by the template itself.
        """

        for template in self.prompts:
            if self.prompts[template]["prompt_token_lenght"] == -1:
                with  get_openai_callback() as cb:

                    #set all template fields as '' to avoid problems with the token count
                    dict_vars = { var: "" for var in self.prompts[template]["input_variables"] }

                    self.model( self.prompts[template]["template"].format(**dict_vars) )
                    self.prompts[template]["prompt_token_lenght"] = cb.prompt_tokens


    def load_model(self) -> None:
        """Loads LLama model"""
        model  = OpenAI(**self.options)
        self.model = model

    def load_chain(self, template: int = 0) -> None:
        self.load_model()
        prompt: PromptTemplate = PromptTemplate(
            input_variables = self.prompts[template]["input_variables"],
            template = self.prompts[template]["template"]
        )
        llm_chain: LLMChain = LLMChain(
            llm=self.model,
            prompt=prompt
        )
        self.llm_chain = llm_chain


def main():

    average_number_of_tokens_per_sentence = 27
    desired_number_of_sentences_per_file = 15
    max_tokens = desired_number_of_sentences_per_file*average_number_of_tokens_per_sentence
    context_window_size = 4e3

    llm = LLM({
        "openai_api_key": OPEN_AI_API_KEY,
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "presence_penalty": 0.1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
    })

    template = 0
    llm.load_chain(template)

    filename = PROJECTS_PATH + "Arquitectura/ALU.py"
    dh = DocumentHandler()

    with open(filename, "r") as f:
        
        #get the template size and calculate the code token size to use
        template_size = llm.prompts[template]["prompt_token_lenght"]
        code_token_size = (context_window_size - template_size)

        docs = dh.chunk_document(filename, f.read(), code_token_size)
        
        for doc in docs:
            response = llm.llm_chain.run(doc)
            dh.save_response_for_file(filename, response)

if __name__ == "__main__":
    main()
