import os
from dotenv import load_dotenv
from langchain.llms.openai import OpenAI
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from  document_handler import DocumentHandler
from prompt_handler import PromptHandler

#some important enviroment variables
load_dotenv()
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")

#https://python.langchain.com/docs/modules/model_io/models/llms/token_usage_tracking

class LLM:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.model = None
        self.llm_chain = None
        self.load_model()


    def load_model(self) -> None:
        """Loads LLama model"""
        model  = OpenAI(**self.options)
        self.model = model

    def load_chain(self, template: dict[str, any]) -> None:
        self.load_model()

        prompt: PromptTemplate = PromptTemplate(
            input_variables = template["input_variables"],
            template = template["template"]
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

    model_name = "gpt-3.5-turbo"

    llm = LLM({
        "openai_api_key": OPEN_AI_API_KEY,
        "model_name": model_name,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "presence_penalty": 0.1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
    })


    filename = PROJECTS_PATH + "Arquitectura/ALU.py"
    dh = DocumentHandler()
    ph = PromptHandler(model_name=model_name)

    template = ph.get_raw_template(template=0)
    llm.load_chain(template=template)


    with open(filename, "r") as f:
        
        #get the template size and calculate the code token size to use
        template_size = template["prompt_token_lenght"]
        code_token_size = (context_window_size - template_size)

        docs = dh.chunk_document(filename, f.read(), code_token_size)
        
        for doc in docs:
            response = llm.llm_chain.run(doc)
            dh.save_response_for_file(filename, response)

if __name__ == "__main__":
    main()
