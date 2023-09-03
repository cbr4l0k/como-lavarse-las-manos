import os
from dotenv import load_dotenv
from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

#some important enviroment variables
load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")
GRAMMAR_PATH = os.getenv("GRAMMAR_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")

#Possible TODO:
#1. yeah, we split the code into semantically relevant chunks, but then what?
#what do we do with this chunks, do we ask for a summary of each specific chunk
#and then join all the summaries and with that we try to build a description?
#which should also use this approach of chunking beause it can be way too long?

#2. if not (1) what then?

#3. code the document handler, so that the LLM class has noting to do with handling documents, or outputs of
#the model

#4. join the file manager with the document handler.

class LLM:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.Llama_model = None
        self.llm_chain = None
        self.prompts = {"t1": """Assistant is designed to receive a python file, identify which dependencies the file
                                 uses and a brief explanation of what the file contains. Assistant must return a json 
                                 with this fields:
                                 "dependencies": [list of dependencies names, this are the external imports or packages 
                                 the code uses, any standard library or external library is written as: 'pip#library'],
                                 "explanation": 'short code explanation highlighting main features, key classes and
                                  functions.'"" For this given file generate the json ONLY, File received: {code}"""}


    def load_model(self) -> None:
        """Loads LLama model"""
        # callback_manager: CallbackManager = CallbackManager([StreamingStdOutCallbackHandler()])

        Llama_model: LlamaCpp = LlamaCpp(**self.options)
        self.Llama_model = Llama_model

    def load_chain(self):
        self.load_model()
        prompt: PromptTemplate = PromptTemplate(
            input_variables=["code"],
            template=self.prompts["t1"]
        )
        llm_chain: LLMChain = LLMChain(
            llm=self.Llama_model,
            prompt=prompt
        )
        self.llm_chain = llm_chain


def main():

    average_number_of_tokens_per_sentence = 27
    desired_number_of_sentences_per_file = 20
    max_tokens = desired_number_of_sentences_per_file*average_number_of_tokens_per_sentence

    llm = LLM({
        "model_path": MODEL_PATH,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "n_gpu_layers": 400,
        "n_batch": 4096,
        "top_p": 1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
        "grammar_path": GRAMMAR_PATH,
    })
    llm.load_chain()

    with open("/home/lok/devsavant/langchain/como-lavarse-las-manos-master/Arquitectura/Calculator.py", "r") as f:
        code = f.read()

    response = llm.llm_chain.run(code)
    with open("response.json", "w") as f:
        f.write(response)


if __name__ == "__main__":
    main()
