import json
import os
from LLMManager import LLM, default_llm
from dotenv import load_dotenv

load_dotenv()
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")


def load_file_content(file_path):
    with open(PROJECTS_PATH+file_path, "r") as f:
        return f.read()


class Report:
    def __init__(self, project_path, force_generate_report=False) -> None:
        self.project_path = project_path
        self.report = None
        self.load_report()
        self.ext_dependencies = []
        self.LLM = default_llm()

    def load_report(self):
        # check if the file named "filesreport.json" exists
        # if it does, load it
        # if it doesn't, generate it
        if os.path.exists(f"{OUTPUTS_PATH}/filesreport.json"):
            with open(f"{OUTPUTS_PATH}/filesreport.json", "r") as f:
                self.report = json.load(f)
        else:
            self.generate_initial_report()

    def generate_initial_report(self):
        """
            Generates a json report of the project tree.
        """

        os.system(
            f"tree {self.project_path} -J --gitignore | python3 -m json.tool > {OUTPUTS_PATH}/filesreport.json")
        self.load_json_report(f"{OUTPUTS_PATH}/filesreport.json")

    def ext_dependencies_response_handler(self, ext_deps: list):
        for dep in ext_deps:
            if dep not in self.ext_dependencies and not dep.startswith("int."):
                self.ext_dependencies.append(dep)

    def add_ext_dependencies_to_report(self):
        root_directory = self.project_path.split("/")[-1]
        for dep in self.ext_dependencies:
            self.report[0]["contents"].append({
                "type": "External dependency",
                "name": dep,
                "full_path": f"{root_directory}/{dep}",
                "dependencies": [],
                "explanation": ""
            })

    def complete_report_helper(self, directory: dict, root: str):
        if directory["type"] == "directory":
            for child in directory["contents"]:
                self.complete_report_helper(child, f"{root}{directory['name']}/")
        elif directory["type"] == "file":
            if not directory["name"].endswith(".py"):
                return
            directory["full_path"] = f"{root}{directory['name']}"
            response = self.LLM.generate_response(directory["full_path"], load_file_content(directory["full_path"]))
            print("---------------response-----------------")
            print(response)
            # response = {"dependencies": "dependencies", "explanation": "explanation"}
            directory["dependencies"] = response["dependencies"]
            directory["explanation"] = response["explanation"]
            self.ext_dependencies_response_handler(response["dependencies"])

    def complete_report(self):
        """
            This function is supposed to take the report and complete it with the response of the model.
        """
        if self.report is None:
            raise Exception("No report loaded")

        self.complete_report_helper(self.report[0], '')
        self.add_ext_dependencies_to_report()
        with open(f"{OUTPUTS_PATH}/filesreport.json", "w") as f:
            json.dump(self.report, f, indent=4)

        # with open(f"{OUTPUTS_PATH}/ext_dependencies.json", "w") as f:
        #     json.dump(self.ext_dependencies, f, indent=4)


    def load_json_report(self, json_path):
        with open(json_path, "r") as f:
            self.report = json.load(f)
        self.report[0]["name"] = self.project_path.split("/")[-1]





if __name__ == "__main__":
    report = Report("/home/dleyvacastro/Documents/devsavant/Langchain/testing_projects/simpleModuleWithScreenRawMaticas")
    report.complete_report()