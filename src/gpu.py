from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

MODEL_PATH = "/home/dleyvacastro/Documents/devsavant/Langchain/model.bin"
GRAMAR_PATH = "/home/dleyvacastro/Documents/devsavant/Langchain/json.gbnf"

def create_prompt() -> PromptTemplate:
    """Creates a prompt template"""
    # _DEFAUT_TEMPLATE: str = """Assistant is designed to receive a piece of code and return a brief explanation of what it does (no more than 2 lines).
    # Code to explain: {code}
    # Assistant:"""
    _DEFAUT_TEMPLATE: str = """Assistant is designed to recieve a python file, identify which dependencies the file
    uses and a brief explanation of what the file contains. Assistant must return a json format like this:
    "dependencies": [],
    "explanation": ""

    File recived: {code}"""

    # _DEFAUT_TEMPLATE: str = """
    # Given this python file: {code}
    # create a brief explanation of what the file contains and the dependencies it uses.
    # """
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["code"],
        template=_DEFAUT_TEMPLATE
    )
    return prompt

def load_model() -> LLMChain:
    """Loads LLama model"""
    callback_manager: CallbackManager = CallbackManager([StreamingStdOutCallbackHandler()])
    n_gpu_layers = 200
    n_batch = 4096

    Llama_model: LlamaCpp = LlamaCpp(
        model_path=MODEL_PATH,
        temperature=0,
        max_tokens=500,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        top_p=1,
        callback_manager=callback_manager,
        # f16_kv=True,
        # grammar_path=GRAMAR_PATH,
        verbose=True,
    )

    prompt: PromptTemplate = create_prompt()
    llm_chain: LLMChain = LLMChain(
        llm=Llama_model,
        prompt=prompt
    )
    return llm_chain

def process_code(code: str, llm_chain: LLMChain) -> str:
    response: str = llm_chain.run(code)
    return response

def main():
    llm_chain = load_model()

    with open("./Arquitectura/Operations/Divide.py", "r") as f:
        code: str = f.read()
    # timeit the process_code function
    response: str = process_code(code, llm_chain)
    with open("response.txt", "w") as f:
        f.write(response)



if __name__ == "__main__":
    main()
