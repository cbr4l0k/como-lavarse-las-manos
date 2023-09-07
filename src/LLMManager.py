import json
import os
from dotenv import load_dotenv
from langchain.llms.openai import OpenAI
from langchain import PromptTemplate, LLMChain
from langchain.chains import ConversationChain
from langchain.memory import ConversationKGMemory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from FileHandler import FileHandler
from prompt_handler import PromptHandler

# some important enviroment variables
load_dotenv()
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")
DEFAULT_LLM = os.getenv("DEFAULT_LLM")


class LLM:
    def __init__(self, options: dict) -> None:
        self.model = None
        self.llm_chain = None
        self.context_window_size = None
        self.options = options
        self.prompt_handler = PromptHandler(model_name=self.options["model_name"])

        self.load_model()
        self.file_handler = FileHandler()
        self.context_window_size = 16e3

    def set_context_window_size(self, context_window_size: int) -> None:
        self.context_window_size = context_window_size

    def load_model(self) -> None:
        """Loads LLama model"""
        model = OpenAI(**self.options)
        self.prompt_handler.set_model(model_name=self.options["model_name"])
        self.model = model

    def load_chain(self, template: dict[str, any], requires_memory: bool = False) -> None:
        self.load_model()
        prompt: PromptTemplate = PromptTemplate(
            input_variables=template["input_variables"],
            template=template["template"]
        )

        llm_chain: LLMChain = LLMChain(
            llm=self.model,
            prompt=prompt,
            verbose=True,
        )

        self.llm_chain = llm_chain

    def generate_response(self, file_full_path: str, code: str) -> str:

        # estimate the number of tokens for the code
        code_token_size = (self.context_window_size - self.prompt_handler.longest_prompt_lenght)

        # chunk the document based on the estimated number of tokens available for the code
        docs = self.file_handler.chunk_document(file_full_path, code, code_token_size)

        # define the response
        response = None

        # if the document is too small, just run it
        if len(docs) == 1:
            template = self.prompt_handler.get_raw_template(template=0)
            self.load_chain(template=template)
            response = self.llm_chain.run(docs[0].page_content)

        # if the document is too big, chunk it and run it
        elif len(docs) > 1:
            template = self.prompt_handler.get_raw_template(template=1)
            self.load_chain(template=template, requires_memory=True)

            responses = []

            for doc in docs:
                response = self.llm_chain.run(doc.page_content)
                responses.append(response)

            # combine the responses and save them
            template = self.prompt_handler.get_raw_template(template=2)
            self.load_chain(template=template, requires_memory=True)

            response = self.llm_chain.run(responses)

        print(response)
        response_json = json.loads(response)
        return response_json
    
    def generate_cohesion_coupling_analysis(self, json_report: str) -> str:

        """
            Given a json report of a project, with the parcial dependencies and explainations.
            generate a cohesion and coupling analysis.
        """

        template = self.prompt_handler.get_raw_template(template=3)
        prompt = self.prompt_handler.get_prompt(template=3, json_reports=json_report)
        prompt_len = self.prompt_handler.get_prompt_token_lenght(prompt)

        # if the prompt is really big (bigger than the context window size) then load 
        # the gpt which has a bigger context window size

        if prompt_len > self.context_window_size:
            print("prompt is too big, loading gpt-3.5-turbo-16k")
            self.options["model_name"] = "gpt-3.5-turbo-16k"
            self.load_model()
            self.set_context_window_size(16e3)

            self.load_chain(template=template)
            response = self.llm_chain.run(prompt)
        
        else:
            print("prompt is not too big, loading gpt-3.5-turbo")
            self.options["model_name"] = "gpt-3.5-turbo"
            self.load_model()
            self.set_context_window_size(4e3)

            self.load_chain(template=template)
            response = self.llm_chain.run(prompt)
        
        #before returning the response, go back to the original cheaper model
        self.options["model_name"] = "gpt-3.5-turbo"
        self.set_context_window_size(4e3)

        self.load_model()
        return response
        


def default_llm():
    average_number_of_tokens_per_sentence = 27
    desired_number_of_sentences_per_file = 30
    max_tokens = desired_number_of_sentences_per_file * average_number_of_tokens_per_sentence
    context_window_size = 4e3

    model_name = DEFAULT_LLM

    llm = LLM({
        "openai_api_key": OPEN_AI_API_KEY,
        "model_name": model_name,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "presence_penalty": 0.1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
    })
    return llm


def main():
    average_number_of_tokens_per_sentence = 27
    desired_number_of_sentences_per_file = 30
    max_tokens = desired_number_of_sentences_per_file * average_number_of_tokens_per_sentence
    context_window_size = 16e3

    model_name = DEFAULT_LLM

    llm = LLM({
        "openai_api_key": OPEN_AI_API_KEY,
        "model_name": model_name,
        "temperature": 0.0,
        "max_tokens": max_tokens,
        "presence_penalty": 0.1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
    })

    # read a document from the project path
    # and test running the process_code function

    file = f"{PROJECTS_PATH}/simpleModuleWithScreenRawMaticas/dependencies/writer.py"
    #file = f"{OUTPUTS_PATH}/filesreport.json"

    with open(file, "r") as f:
        code = f.read()
        response = llm.generate_response(file, code)
        #response = llm.generate_cohesion_coupling_analysis(code)
        print(response)


if __name__ == "__main__":
    main()
