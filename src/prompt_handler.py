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

                                 "dependencies": [list of dependencies names, external libraries as 'ext.library' and internal
                                 libraries as 'int.library' are accepted, for example: 'ext.numpy', 'int.my_library.plotter', 
                                 include imports like 'from lib import something',
                                 if 'from lib import something' write it as '(int or ext).lib', 
                                 if 'from lib.sublib import something' write it as '(int or ext).lib.sublib' and so on],
                                 "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                 and methods. If makes sense infer behavior from method names.'""

                                 give me the json ONLY, terminate the json, give me a well formated json, be short and concise, File received: {code}""",
                            "input_variables": ["code", ],
                            "prompt_token_lenght": -1
                            },
                        1: {"template": """Given this new fragment of code of a bigger file, identify which dependencies the file uses and do
                                           a brief explanation of what the file contains. You must return a json with this fields:

                                           "dependencies": [list of dependencies names, external libraries as 'ext.library' and internal
                                           libraries as 'int.library' are accepted, for example: 'ext.numpy', 'int.my_library.plotter', 
                                           include imports like 'from lib import something',
                                           if 'from lib import something' write it as '(int or ext).lib', 
                                           if 'from lib.sublib import something' write it as '(int or ext).lib.sublib' and so on],
                                           "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                           and methods, if makes sense infer behavior from method names'""

                                           give me the json ONLY, terminate the json, give me a well formated json, be short and concise, File received: {code}""",
                            "input_variables": ["code", ],
                            "prompt_token_lenght": -1
                            },
                        2: {"template": """Now that you have identified the dependencies and the explanation of the file in different
                                           json chunks, you must unify the dependencies and explanations in a single json file.
                                           You are a pro bot developer and can take into account that the dependencies and explanations
                                           don't have repeated values. You must return a json with this fields:

                                           "dependencies": [list of dependencies names, external libraries as 'ext.library' and internal
                                           libraries as 'int.library' are accepted, for example: 'ext.numpy', 'int.my_library.plotter', 
                                           include imports like 'from lib import something',
                                           if 'from lib import something' write it as '(int or ext).lib', 
                                           if 'from lib.sublib import something' write it as '(int or ext).lib.sublib' and so on],
                                           "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                           and methods, if makes sense infer behavior from method names. This explaination condenses the
                                           other explainations and takes the knowledge of all of them.'""

                                            give me the json ONLY, terminate the json, give me a well formated json, be short and concise, Jsons recieved: {json_reports}""",
                            "input_variables": ["json_reports", ],
                            "prompt_token_lenght": -1
                            },
                        3: {"template": """Given this python analysis file of a project, identify the level of coupling in the project and
                                           the level of cohesion in the project. You must explain your answer, the reason why you think
                                           the project has that level of coupling and cohesion. You must return a json with this fields: 
                            
                                           "coupling": 'low, medium or high, and the reason why you think the project has that level of coupling',
                                           "cohesion": 'low, medium or high, and the reason why you think the project has that level of cohesion'
                                           "explanation":'short explanation of why you think the project has that level of coupling and cohesion, 
                                                          also explain if this is a good thing or a bad thing, and why. '""

                                            give me the json ONLY and dont forget to explain your desicion and it's implications, 
                                            terminate the json, give me a well formated json, be short and concise, File received: {json_reports}""",
                            "input_variables": ["json_reports", ],
                            "prompt_token_lenght": -1
                            }
                        }

        self.longest_prompt_lenght = -1
        self.set_model(model_name=model_name)
        self.set_largest_prompt_token_lenght()

    def set_largest_prompt_token_lenght(self) -> None:
        """
            Sets the largest prompt token lenght for all the templates
        """
        for template in self.prompts:
            if self.prompts[template]["prompt_token_lenght"] > self.longest_prompt_lenght:
                self.longest_prompt_lenght = self.prompts[template]["prompt_token_lenght"]

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

    def get_prompt_token_lenght(self, prompt: str) -> int:
        """
            Returns the prompt token lenght for the given prompt
        """
        return len(self.encoding.encode(prompt))

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
        dict_vars = {var: "" for var in self.prompts[template]["input_variables"]}
        return self.prompts[template]["template"].format(**dict_vars)