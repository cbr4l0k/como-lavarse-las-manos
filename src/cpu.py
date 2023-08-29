from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

MODEL_PATH = "/home/dleyvacastro/Documents/devsavant/Langchain/model.bin"


def load_model() -> LlamaCpp:
    """Loads LLama model"""
    callback_manager: CallbackManager = CallbackManager([StreamingStdOutCallbackHandler()])

    Llama_model: LlamaCpp = LlamaCpp(
        model_path=MODEL_PATH,
        temperature=0.5,
        max_tokens=2000,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True,
    )
    return Llama_model


def main():
    llm = load_model()

    model_prompt: str = """
    Question: which is the most popular programming language?
    """
    response: str = llm(model_prompt)
    print(response)


if __name__ == "__main__":
    main()