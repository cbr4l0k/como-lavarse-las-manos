import os
import json
import tiktoken
from hashlib import sha256
from dotenv import load_dotenv

load_dotenv()
CONFIG_PATH = os.getenv("CONFIG_PATH")

class PromptHandler:
        

    def __init__(self, model_name: str):

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
                            "prompt_token_lenght": -1
                            }
                        }
        self.set_model(model_name=model_name)


    def set_model(self, model_name: str) -> None:
        """
            Sets the model name and encoding for the prompt handler.
            And with that it gets the prompt token lenght for each template.
        """
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(self.model_name)
        self.set_token_lenght()
    
    def get_raw_template(self, template: int = 0) -> dict:
        """
            Returns the raw prompt for the given template
        """
        return self.prompts[template]
    
    def get_prompt(self, template: int = 0, **kwargs) -> str:
        """
            Returns the prompt for the given template, 
            if the template has input variables, they must be passed as kwargs
        """
        return self.prompts[template]["template"].format(**kwargs)

    def set_token_lenght(self) -> None:
        """
            Sets the token lenght for all the templates using the current model encoding
        """

        for template in self.prompts:
            white_spaced_template = self.white_spaced_template(template=template)
            self.prompts[template]["prompt_token_lenght"] = len(self.encoding.encode(white_spaced_template))


    def white_spaced_template(self, template: int = 0) -> str:
        """
            Returns the template with all the input variables replaced by an empty string
        """
        dict_vars = { var: "" for var in self.prompts[template]["input_variables"] }
        return self.prompts[template]["template"].format(**dict_vars)