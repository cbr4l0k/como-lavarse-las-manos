import os
from dotenv import load_dotenv
from langchain.llms.openai import OpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from FileHandler import FileHandler
from prompt_handler import PromptHandler

load_dotenv()
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")

llm = OpenAI(temperature=0.1,
             openai_api_key = OPEN_AI_API_KEY,
             model_name="gpt-3.5-turbo",
             max_tokens=400,
             presence_penalty=0.1,
             callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationKGMemory


ph = PromptHandler("gpt-3.5-turbo")
template = ph.get_raw_template(1)["template"]            

prompt = PromptTemplate(input_variables=["input", "history"], template=template)
conversation_with_kg = ConversationChain(
    llm=llm, verbose=True, prompt=prompt, memory=ConversationKGMemory(llm=llm)
)
print(conversation_with_kg.predict(input="""from ALU import ALU

class Calculator:
    def __init__(self) -> None:
        self.alu: ALU = ALU()
        self.operator: bool = False

    def menu(self) -> None:
        finished: bool = False
        while 1:
            if self.operator:
                self.operator = False
                finished = self.alu.process_operator()
                if finished:
                    break
            else:
                self.operator = True
                self.alu.process_operand()

    def main(self) -> None:
        self.menu()


if __name__ == '__main__':
    calc = Calculator()
    calc.main()

""",))