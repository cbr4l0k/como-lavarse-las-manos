from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class LLM:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.Llama_model = None
        self.llm_chain = None
        self.prompts = {
            "t1": """Assistant is designed to receive a python file, identify which dependencies the file
    uses and a brief explanation of what the file contains. Assistant must return a json with this fields:
    
    "dependencies": [list of dependencies names, this are the external imports or packages the code uses],
    "explanation": 'short code explanation highlighting main features, key classes and functions.'
   
     ""

    For this given file generate the json ONLY, File received: {code}"""
    }

    def load_model(self) -> LlamaCpp:
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
    desired_number_of_sentences_per_file = 30
    max_tokens = desired_number_of_sentences_per_file*average_number_of_tokens_per_sentence

    llm = LLM({
        "model_path": "/home/lok/devsavant/langchain/como-lavarse-las-manos-master/model.bin",
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "n_gpu_layers": 400,
        "n_batch": 4096,
        "top_p": 1,
        "callback_manager": CallbackManager([StreamingStdOutCallbackHandler()]),
        "verbose": True,
        "grammar_path": "/home/lok/devsavant/langchain/como-lavarse-las-manos-master/json.gbnf"
    })
    llm.load_chain()

    with open("/home/lok/devsavant/langchain/como-lavarse-las-manos-master/Arquitectura/Calculator.py", "r") as f:
        code = f.read()

    response = llm.llm_chain.run(code)
    with open("response.json", "w") as f:
        f.write(response)


if __name__ == "__main__":
    main()
