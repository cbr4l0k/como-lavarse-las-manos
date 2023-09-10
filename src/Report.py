import json
import os
from datetime import datetime
from LLMManager import LLM, default_llm
from dotenv import load_dotenv

load_dotenv()
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")


# def load_file_content(file_path: str) -> str:
#     """
#         Loads the content of a file.
#
#         Args:
#         ------
#             file_path: str
#
#         Returns:
#         --------
#             str
#     """
#     with open(PROJECTS_PATH + file_path, "r") as f:
#         return f.read()


class Report:
    def __init__(self, project_path) -> None:
        """
            Constructor of the Report class.

            Args:
            ------
                project_path: str

            Returns:
            --------
                None
        """
        self.files = None
        self.project_path: str = project_path
        self.report: dict = {}
        self.find_all_files()
        self.generate_initial_report()
        self.ext_dependencies: dict = {}
        self.int_dependencies: dict = {}
        self.LLM = default_llm(self.project_path)

    def load_file_content(self, file_path: str) -> str:
        """
            Loads the content of a file.

            Args:
            ------
                file_path: str

            Returns:
            --------
                str
        """
        fp_list = file_path.split("/")
        fp_list.pop(0)
        file_path = "/".join(fp_list)
        with open(self.project_path + "/" + file_path, "r") as f:
            return f.read()

    def find_all_files(self):
        """
            Finds all the files in the project tree.

            Args:
            ------
                None

            Returns:
            --------
                None
        """
        files = []
        for root, _, filenames in os.walk(self.project_path):
            for filename in filenames:
                files.append(filename)
        self.files = files

    def generate_initial_report(self) -> None:
        """
            Generates a json report of the project tree.

            Args:
            ------
                None
            Returns:
            --------
                None
        """

        os.system(f"tree {self.project_path} -J --gitignore | python3 -m json.tool > {OUTPUTS_PATH}filesreport.json")
        os.system(f"tree {self.project_path} --gitignore > {OUTPUTS_PATH}filesreport.txt")
        self.load_json_report(f"{OUTPUTS_PATH}filesreport.json")

    def dependencies_response_handler(self, deps: list) -> None:
        """
            Identifies the external dependencies

            Args:
            ------
                ext_deps: list

            Returns:
            --------
                None
        """
        for dep in deps:
            # if dep not in self.ext_dependencies and not dep.startswith("int/"):
            #     self.ext_dependencies.append(dep)
            if dep.startswith("int/"):  # internal dependency
                if dep not in self.int_dependencies.keys():
                    dep = dep.replace(".py", "")
                    self.int_dependencies[dep] = 1
                else:
                    self.int_dependencies[dep] += 1
            elif dep.startswith("ext/"):
                if dep not in self.ext_dependencies.keys():
                    dep = dep.replace(".py", "")
                    self.ext_dependencies[dep] = 1
                else:
                    self.ext_dependencies[dep] += 1

    def add_internal_dependencies_to_report_helper(self, directory):
        """
            Adds the internal dependencies to the report

            Args:
            ------
                directory: dict

            Returns:
            --------
                None
        """
        if directory["type"] == "directory":
            for child in directory["contents"]:
                self.add_internal_dependencies_to_report_helper(child)
        elif directory["type"] == "file":
            if not directory["name"].endswith(".py"):
                return
            # directory["times_called"] = self.int_dependencies[directory["full_path"]]
            full_path_list = directory["full_path"].split("/")
            full_path_list.pop(0)
            full_path_list.insert(0, "int")
            name = "/".join(full_path_list)

            if name in self.int_dependencies.keys():
                directory["times_called"] = self.int_dependencies[name]
            elif name+".py" in self.int_dependencies.keys():
                directory["times_called"] = self.int_dependencies[name+".py"]
            elif name[:-3] in self.int_dependencies.keys():
                directory["times_called"] = self.int_dependencies[name[:-3]]



    def add_ext_dependencies_to_report(self) -> None:
        """
            Adds the external dependencies to the report

            Args:
            ------
                None

            Returns:
            --------
                None
        """
        root_directory = self.project_path.split("/")[-1]
        for dep in self.ext_dependencies:
            self.report[0]["contents"].append({
                "type": "External dependency",
                "name": dep,
                "times_called": self.ext_dependencies[dep],
                "full_path": f"{root_directory}/{dep}",
                "dependencies": [],
                "explanation": ""
            })

    def complete_report_helper(self, directory: dict, root: str):
        """
            This function is supposed to take the report and complete it with the response of the model.

            Args:
            ------
                directory: dict
                root: str

            Returns:
            --------
                None
        """
        if directory["type"] == "directory":
            if "contents" not in directory.keys():
                directory["contents"] = []
            for child in directory["contents"]:
                self.complete_report_helper(child, f"{root}{directory['name']}/")
        elif directory["type"] == "file":
            if not directory["name"].endswith(".py"):
                return
            directory["full_path"] = f"{root}{directory['name']}"
            file_id = directory["full_path"].split("/")
            file_id[0] = "int"
            file_id = "/".join(file_id)
            directory["id"] = file_id
            response = self.LLM.generate_response(directory["full_path"], self.load_file_content(directory["full_path"]))
            # print("---------------response-----------------")
            # print(response)
            # response = {"dependencies": "dependencies", "explanation": "explanation"}
            for i in range(len(response["dependencies"])):
                # remove the .py extension
                response["dependencies"][i] = response["dependencies"][i].replace(".py", "")
                if response["dependencies"][i].split("/")[-1]+".py" not in self.files:
                    print(f"WARNING: {response['dependencies'][i]} not found in the project tree")
                    response["dependencies"][i] = response["dependencies"][i].replace("int/", "ext/")

            directory["dependencies"] = response["dependencies"]
            directory["explanation"] = response["explanation"]
            self.dependencies_response_handler(response["dependencies"])

    def remove_py_extension(self):
        """
            This function is supposed to take the report and complete it with the response of the model.

            Args:
            ------
                None

            Returns:
            --------
                None
        """
        if self.report is None:
            raise Exception("No report loaded")
        self.remove_py_extension_helper(self.report[0])

    def add_directory_information_helper(self, directory):
        """
            This function is supposed to take the report and complete it with the response of the model.

            Args:
            ------
                directory: dict

            Returns:
            --------
                None
        """
        if directory["type"] == "directory":

            current_directory_list: list = []
            for i in directory["contents"]:
                if i["type"] == "file":
                    current_directory_list.append(i)
                else:
                    current_directory_list.append({
                        "name": i["name"],
                        "type": "directory"
                    })
                    self.add_directory_information_helper(i)

            response = self.LLM.generate_explaination_for_directory(current_directory_list)
            # response = "generic description"
            directory["explanation"] = response

    def complete_report(self):

        """
            This function is supposed to take the report and complete it with the response of the model.

            Args:
            ------
                None

            Returns:
            --------
                None
        """
        if self.report is None:
            raise Exception("No report loaded")

        self.complete_report_helper(self.report[0], '')
        self.add_directory_information_helper(self.report[0])
        self.add_internal_dependencies_to_report_helper(self.report[0])
        self.add_ext_dependencies_to_report()
        self.remove_py_extension()
        self.add_aditional_info()
        self.save_report()

        # with open(f"{OUTPUTS_PATH}/ext_dependencies.json", "w") as f:
        #     json.dump(self.ext_dependencies, f, indent=4)

    def load_json_report(self, json_path):
        """
            Loads the json report into the report attribute.

            Args:
            ------
                json_path: str

            Returns:
            --------
                None
        """
        with open(json_path, "r") as f:
            self.report = json.load(f)
        self.report[0]["name"] = self.project_path.split("/")[-1]

    def remove_py_extension_helper(self, directory: dict):
        """
            Removes the .py extension from the files in the report.

            Args:
            ------
                directory: dict

            Returns:
            --------
                None
        """
        if directory["type"] == "directory":
            directory["children"] = directory["contents"]
            del directory["contents"]
            for child in directory["children"]:
                self.remove_py_extension_helper(child)
        elif directory["type"] == "file":
            if not directory["name"].endswith(".py"):
                return
            directory["name"] = directory["name"].replace(".py", "")
            directory["full_path"] = directory["full_path"].replace(".py", "")
            directory["id"] = directory["id"].replace(".py", "")

    def add_aditional_info(self):
        """
            Adds the cohesion and coupling analysis to the report.

            Args:
            ------
                None

            Returns:
            --------
                None
        """
        response = self.LLM.generate_cohesion_coupling_analysis(self.report)
        self.report[1]["coupling"] = response["coupling"]
        self.report[1]["cohesion"] = response["cohesion"]
        self.report[1]["explanation"] = response["explanation"]

    def save_report(self):
        """
            Saves the report in the outputs folder.

            Args:
            ------
                None

            Returns:
            --------
                None
        """
        with open(
                f"{OUTPUTS_PATH}reports/filesreport_{self.project_path.split('/')[-1]}_{datetime.now().strftime('%m_%d_%H_%M')}.json",
                "w") as f:
            json.dump(self.report, f, indent=4)

        with open(f"{OUTPUTS_PATH}reports/finalreport.json", "w") as f:
            json.dump(self.report, f, indent=4)


if __name__ == "__main__":
    report = Report(f"{PROJECTS_PATH}Arquitectura")
    report.complete_report()
    # report.find_all_files()
    # print(report.files)