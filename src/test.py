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


class LLM:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.model = None
        self.llm_chain = None
        self.load_model()

    def load_model(self) -> None:
        """Loads LLama model"""
        model = OpenAI(**self.options)
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


def main():
    average_number_of_tokens_per_sentence = 27
    desired_number_of_sentences_per_file = 15
    max_tokens = desired_number_of_sentences_per_file * average_number_of_tokens_per_sentence
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

    # get the documents
    dh = FileHandler()
    dh.generate_json_report(f"{PROJECTS_PATH}/simpleModuleWithScreenRawMaticas/dependencies")
    docs_iter = dh.read_files_from_project_tree()
    
    #get and load the template
    ph = PromptHandler(model_name=model_name)


    for file in docs_iter:

        filename, code, gid = file

        # estimate the number of tokens for the code
        code_token_size = (context_window_size - ph.longest_prompt_lenght)
        
        # chunk the document based on the estimated number of tokens
        docs = dh.chunk_document(filename, code, code_token_size)

        # if the document is too small, just run it
        if len(docs) == 1:
            template = ph.get_raw_template(template=0)
            llm.load_chain(template=template)
            response = llm.llm_chain.run(docs[0].page_content)
            dh.save_response_for_file(filename, response, gid)

        # if the document is too big, chunk it and run it
        elif len(docs) > 1:
            template = ph.get_raw_template(template=1)
            llm.load_chain(template=template, requires_memory=True)

            responses = []

            for doc in docs:
                response = llm.llm_chain.run(doc.page_content)
                responses.append(response)

            # combine the responses and save them
            template = ph.get_raw_template(template=2)
            llm.load_chain(template=template, requires_memory=True)

            response = llm.llm_chain.run(responses)
            dh.save_response_for_file(filename, response, gid)
        

if __name__ == "__main__":
    main()
