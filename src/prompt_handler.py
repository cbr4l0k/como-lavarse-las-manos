import os
import json
import tiktoken
from hashlib import sha256
from dotenv import load_dotenv

load_dotenv()
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")


class PromptHandler:
    """
        Class for handling the prompts for the LLM.

        Class Attributes:
            outputs_path (str): The outputs path.

        Attributes:
            model_name (str): The model name.
            encoding (tiktoken.Encoding): The encoding for the model.
            prompts (dict): The prompts for the LLM.
            longest_prompt_lenght (int): The longest prompt lenght for all the prompts.

        Methods:

            - load_initial_filesreport: Loads the initial files report.
            - set_largest_prompt_token_lenght: Sets the largest prompt token lenght for all the templates.
            - set_model: Sets the model name and encoding for the prompt handler.
            - get_raw_template: Returns the raw prompt for the given template.
            - get_prompt: Returns the prompt for the given template, if the template has input variables, they must be passed as kwargs.
            - get_prompt_token_lenght: Returns the prompt token lenght for the given prompt.
            - set_token_lenght: Sets the token lenght for all the templates using the current model encoding.
            - white_spaced_template: Returns the template with all the input variables replaced by an empty string.
    """

    projects_path = ''

    def __init__(self, model_name: str):
        self.initial_files_report = None
        self.load_initial_filesreport()

        self.prompts = {0: {"template": """Identify which dependencies the file uses and do a brief explanation of what the file contains.
                                           Context we have this tree files:
                                            {}
                                """.format(self.initial_files_report) +
                                """                          
                                You must return a json with this fields:
                                    "dependencies": [list of dependencies names, external libraries as 'ext/library' and internal
                                    libraries 'int/library' are accepted, for example: 'ext/numpy', 'int/my_library/plotter'. Dependencies
                                    are the libraries which the code uses and imports.],
                                    "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                    and methods, if makes sense infer behavior from method names'""

                                For identifying the dependencies you must:
                                    1. Look at the context of the file tree.
                                    2. Idenfitify the dependencies of the code, this is modules or scripts it imports.
                                    3. Check if any identified dependency in the code is or not in the file tree. 
                                       A dependency is internal if for example the code says: 'from my_library.sub_lib import module' 
                                       and there is a folder named 'my_library' in the file tree and a folder or file named 'sub_lib'.
                                    4. If the dependency is not in the file tree, it's external and shuld be written as 'ext/library'
                                       or 'ext/library/sublibrary' and so on. 
                                    5. If the dependency is in the file tree, it's internal and should be written as 'int/library'
                                       or 'int/library/sublibrary' and so on, make sure to add the path to the internal library taking 
                                       as reference the root of the file tree. for example if the file tree is:
                                        root
                                        |---lib
                                        |   |---sub_lib
                                        |       |---module.py
                                        |---file.py

                                        and the file.py says: 'from lib.sub_lib import module', the dependency is internal and should be
                                        written as 'int/lib/sub_lib/module'.

                                    6. DONT INVENT THINGS, IF THE CODE IS NOT IMPORTING SOMETHING DONT ADD IT AS DEPENDENCY. OTHERWISE 
                                    YOU WILL BE PENALIZED, FIRED, AND YOUR FAMILY WILL BE ASHAMED OF YOU. for example, you can not import
                                    your own class from the same file. Don't change the file names, for example if there is a folder or 
                                    file named 'my_library' don't change it to 'my_lib' or 'my_libs' or something different from the tree 
                                    name.

                                 give me the json only, give me a well formated json, be short and concise, don't forget,
                                 the (int or ext)/lib structure, use the file tree as context. Maximum of 60 words as explanation.
                                 Code received: 
                                 
                                 {code}

                                 Think on your response, if for example you have 'from yada.yada.yodo import yuda' don't write
                                 'yada.yada.yodo' as dependency, write 'yada/yada/yodo', 'yada.yada.yodo' is wrong. 
                                 YOUR JSON RESPONSE GOES HERE:""",
                            "input_variables": ["code", ],
                            "prompt_token_lenght": -1
                            },
                        1: {"template": """Given this new fragment of code of a bigger file, identify which dependencies the file uses and do
                                           a brief explanation of what the file contains. 
                                           Context we have this tree files:
                                           {}
                                """.format(self.initial_files_report) +
                                """
                                You must return a json with this fields:
                                    "dependencies": [list of dependencies names, external libraries as 'ext/library' and internal
                                    libraries 'int/library' are accepted, for example: 'ext/numpy', 'int/my_library/plotter'. Dependencies
                                    are the libraries which the code uses and imports.],
                                    "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                    and methods, if makes sense infer behavior from method names'""

                                For identifying the dependencies you must:
                                    1. Look at the context of the file tree.
                                    2. Idenfitify the dependencies of the code, this is modules or scripts it imports.
                                    3. Check if any identified dependency in the code is or not in the file tree. 
                                       A dependency is internal if for example the code says: 'from my_library.sub_lib import module' 
                                       and there is a folder named 'my_library' in the file tree and a folder or file named 'sub_lib'.
                                    4. If the dependency is not in the file tree, it's external and shuld be written as 'ext/library'
                                       or 'ext/library/sublibrary' and so on. 
                                    5. If the dependency is in the file tree, it's internal and should be written as 'int/library'
                                       or 'int/library/sublibrary' and so on, make sure to add the path to the internal library taking 
                                       as reference the root of the file tree. for example if the file tree is:
                                        root
                                        |---lib
                                        |   |---sub_lib
                                        |       |---module.py
                                        |---file.py

                                        and the file.py says: 'from lib.sub_lib import module', the dependency is internal and should be
                                        written as 'int/lib/sub_lib/module'.

                                    6. DONT INVENT THINGS, IF THE CODE IS NOT IMPORTING SOMETHING DONT ADD IT AS DEPENDENCY. OTHERWISE 
                                    YOU WILL BE PENALIZED, FIRED, AND YOUR FAMILY WILL BE ASHAMED OF YOU. for example, you can not import
                                    your own class from the same file. Don't change the file names, for example if there is a folder or 
                                    file named 'my_library' don't change it to 'my_lib' or 'my_libs' or something different from the tree 
                                    name.

                                    give me the json only, give me a well formated json, be short and concise, don't forget,
                                    the (int or ext)/lib structure, use the file tree as context. Maximum of 60 words as explanation.
                                    Code received: 

                                    {code}
                                            
                                    YOUR JSON RESPONSE GOES HERE:""",
                            "input_variables": ["code", ],
                            "prompt_token_lenght": -1
                            },
                        2: {"template": """Now that you have identified the dependencies and the explanation of the file in different
                                           json chunks, you must unify the dependencies and explanations in a single json file.
                                           You are a pro bot developer and can take into account that the dependencies and explanations
                                           don't have repeated values. 
                                           
                                           You must return a json with this fields:

                                           "dependencies": [list of dependencies names, external libraries as 'ext/library' and internal
                                           libraries as 'int/library' are accepted, for example: 'ext/numpy', 'int/my_library/plotter', 
                                           include imports like 'from lib import something',
                                           if 'from lib import something' write it as '(int or ext)/lib', 
                                           if 'from lib.sublib import something' write it as '(int or ext)/lib.sublib' and so on],
                                           "explanation": 'short code explanation highlighting ONLY: main features, key classes, functions 
                                           and methods, if makes sense infer behavior from method names. This explanation condenses the
                                           other explanations and takes the knowledge of all of them.'""

                                           Make sure to give the dependencies in the desired form '(int or ext)/dependency'.
                                           Check for errors and fix them. Maximum of 60 words as explanation.
                                           Jsons reports received: 
                                           
                                           {json_reports}
                                            
                                           YOUR JSON RESPONSE GOES HERE: """,
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
                                            terminate the json, give me a well formated json, be short and concise, File received: {json_reports}.

                                            JSON GOES HERE: """,
                            "input_variables": ["json_reports", ],
                            "prompt_token_lenght": -1
                            }, 
                         4: {"template": """You've been given a json with the fields 'dependencies' and 'explanation', your
                                            work is to correct the json response if needed and return it, you only have to change
                                            the 'dependencies' field, the 'explanation' field is correct.
                             
                                            You must return a json with this fields:

                                            For checking the dependencies you must:
                                                1. Look at the context of the file tree.
                                                2. Idenfitify the dependencies of the file.
                                                3. Check if any identified dependency in the code is or not in the file tree. 
                                                A dependency is internal if for example the code says: 'from my_library.sub_lib import module' 
                                                and there is a folder named 'my_library' in the file tree and a folder or file named 'sub_lib'.
                                                4. If the dependency is not in the file tree, it's external and shuld be written as 'ext/library'
                                                or 'ext/library/sublibrary' and so on. 
                                                5. If the dependency is in the file tree, it's internal and should be written as 'int/library'
                                                or 'int/library/sublibrary' and so on, make sure to add the path to the internal library taking 
                                                as reference the root of the file tree. for example if the file tree is:
                                                    root
                                                    |---lib
                                                    |   |---sub_lib
                                                    |       |---module.py
                                                    |---file.py

                                                and the file.py says: 'from lib.sub_lib import module', the dependency is internal and should be
                                                written as 'int/lib/sub_lib/module'.

                                                6. DONT INVENT THINGS, IF THE CODE IS NOT IMPORTING SOMETHING DONT ADD IT AS DEPENDENCY. OTHERWISE 
                                                YOU WILL BE PENALIZED, FIRED, AND YOUR FAMILY WILL BE ASHAMED OF YOU. for example, you can not import
                                                your own class from the same file. Don't change the file names, for example if there is a folder or 
                                                file named 'my_library' don't change it to 'my_lib' or 'my_libs' or something different from the tree 
                                                name.


                                            The file tree is:
                                            {}""".format(self.initial_files_report) + """

                                            Think on your response, if for example you have 'from yada.yada.yodo import yuda' don't write
                                            'yada.yada.yodo' as dependency, write 'yada/yada/yodo', 'yada.yada.yodo' is wrong. 
                                            Adding the file extension is wrong, for example 'yada/yada/yodo.py' is wrong,
                                            'yada/yada/yodo' is correct. 

                                            Give me the json only, give me a well formated json, be short and concise, don't forget to leave
                                            the 'explanation' field as it is. Change the dependencies which end with '.file_extension' 
                                            to the correct form, delete the '.file_extension' part. 

                                            JSON GOES HERE: \n {json_reports}""",
                                            "input_variables": ["json_reports", ],
                                            "prompt_token_lenght": -1
                         },
                         5: {"template": """You've been given a json file with fields 'dependencies' and 'explanation' for a folder in a project,
                                            your task is to retrieve an explanation this is what the 'explanation' should look like:
                             
                                            "explanation": 'short folder explanation condensing the logic, purpose and explanations of all the 
                                            files inside the folder, including other folders inside the json. Infer behavior from file names and
                                            explanations.'""

                                            {json_reports} 
                             
                                            Remember to give back an explanation only, and the other existing fields.
                                            Maximum of 90 words as explanation. Give it as raw text.
                                            'explanation':
                                            """,    
                             "input_variables": ["json_reports", ],
                             "prompt_token_lenght": -1
                         }
                        }

        self.longest_prompt_lenght = -1
        self.set_model(model_name=model_name)
        self.set_largest_prompt_token_lenght()


    @staticmethod
    def set_projects_path(projects_path: str) -> None:
        """
            Sets the output path for the prompt handler class.

            Args:
            ---------
                output_path (str): The output path.

            Returns:
            ---------
                None
        """
        PromptHandler.projects_path = projects_path

    def load_initial_filesreport(self) -> None:
        """
            Loads the initial files report. This filesreport.txt is the initial files report.
            The 'filesreport.txt' contains the tree output of the 'tree' command runned over
            the folder of interest.

            Args:
            ---------
                None

            Returns:
            ---------
                None
        """
        with open(f"{OUTPUTS_PATH}filesreport.txt", "r") as f:
            self.initial_files_report = f.read()

    def set_largest_prompt_token_lenght(self) -> None:
        """
            This method gets the longest prompt token lenght among all the templates.
            And sets the class attribute 'longest_prompt_lenght' to that value.

            For that the function assumes that the inputs needed for the templates are
            empty strings.

            Args:
            ---------
                None

            Returns:
            ---------
                None
        """
        for template in self.prompts:
            if self.prompts[template]["prompt_token_lenght"] > self.longest_prompt_lenght:
                self.longest_prompt_lenght = self.prompts[template]["prompt_token_lenght"]

    def set_model(self, model_name: str) -> None:
        """
            Sets the model name and encoding for the prompt handler, 
            with that encoding then it goes on to set the token lenght for all the templates.

            Args:
            ---------
                model_name (str): The model name.

            Returns:
            ---------
                None
        """
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(self.model_name)
        self.set_token_lenght()

    def get_raw_template(self, template: int = 0) -> dict:
        """
            Returns the raw prompt for the given template, if 
            the template doesn't exist returns None.

            Args:
            ---------
                template (int): The template number.
            
            Returns:
            ---------
                dict: The raw template for the given template number. This dict contains the template, the input variables, and the prompt token lenght.
        """
        return self.prompts.get(template, None)

    def get_prompt(self, template: int = 0, **kwargs) -> str:
        """
            Returns the prompt for the given template,
            if the template has input variables, they must be passed as kwargs, in 
            order to replace the input variables in the template.

            Args:
            ---------
                template (int): The template number.
                **kwargs: The input variables for the template.
            
            Returns:
            ---------
                str: The prompt for the given template number.
        """
        return self.prompts[template]["template"].format(**kwargs)

    def get_prompt_token_lenght(self, prompt: str) -> int:
        """
            Returns the prompt token lenght for the given prompt.
            For this it uses the current model encoding.

            Args:
            ---------
                prompt (str): The prompt.
            
            Returns:
            ---------
                int: The prompt token lenght.
        """
        return len(self.encoding.encode(prompt))

    def set_token_lenght(self) -> None:
        """
            Sets the token lenght for all the templates using the current model encoding.
            For that the function assumes that the inputs needed for the templates are
            empty strings.

            Args:
            ---------
                None
            
            Returns:
            ---------
                None
        """

        for template in self.prompts:
            white_spaced_template = self.white_spaced_template(template=template)
            self.prompts[template]["prompt_token_lenght"] = len(self.encoding.encode(white_spaced_template))

    def white_spaced_template(self, template: int = 0) -> str:
        """
            Returns the template with all the input variables replaced by an empty string.

            Args:
            ---------
                template (int): The template number.
            
            Returns:
            ---------
                str: The template with all the input variables replaced by an empty string.
        """
        template = self.get_raw_template(template=template)
        dict_vars = {var: "" for var in template["input_variables"]}

        return template["template"].format(**dict_vars)