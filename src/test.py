import os
from dotenv import load_dotenv
from langchain.llms.openai import OpenAI
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

#some important enviroment variables
load_dotenv()
GRAMMAR_PATH = os.getenv("GRAMMAR_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")

class LLM:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.model = None
        self.llm_chain = None
        self.prompts = {"t1": """Assistant is designed to receive a python file, identify which dependencies the file
                                 uses and a brief explanation of what the file contains. Assistant must return a json 
                                 with this fields:
                                 "dependencies": [list of dependencies names, this are the external imports or packages 
                                 the code uses],
                                 "explanation": 'short code explanation highlighting main features, key classes and
                                  functions.'"" For this given file generate the json ONLY, File received: {code}"""}


    def load_model(self) -> None:
        """Loads LLama model"""
        model  = OpenAI(**self.options)
        self.model = model

    def load_chain(self):
        self.load_model()
        prompt: PromptTemplate = PromptTemplate(
            input_variables=["code"],
            template=self.prompts["t1"]
        )
        llm_chain: LLMChain = LLMChain(
            llm=self.model,
            prompt=prompt
        )
        self.llm_chain = llm_chain


def main():

    average_number_of_tokens_per_sentence = 27
    desired_number_of_sentences_per_file = 30
    max_tokens = desired_number_of_sentences_per_file*average_number_of_tokens_per_sentence

    llm = LLM({
        "openai_api_key": OPEN_AI_API_KEY,
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "presence_penalty": 0.1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
    })
    llm.load_chain()

    filename = PROJECTS_PATH + "simpleModuleWithScreenRawMaticas/scheduler.py"
    output = OUTPUTS_PATH + "scheduler_response.json"

    with open(filename, "r") as f:
        code = f.read()

    response = llm.llm_chain.run(code)
    with open(output, "w") as f:
        f.write(response)


if __name__ == "__main__":
    main()
