import json
import os
import logging
from typing import List
from dotenv import load_dotenv
from langchain.text_splitter import (RecursiveCharacterTextSplitter, Language)
from langchain.schema.document import Document

# some important enviroment variables
load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")


class FileHandler:

    """
        This class is supposed to handle the files, individually.
        It will be in charge of reading the files, chunking them, and retrieving the chunks.


        Attributes:
        ----------

        - py_files_paths: List[str]
            The list of paths to the python files.
        - json: dict
            The json report of the files, containing the information about the files, and the chunks.
        
        Methods:
        ----------
        - load_json_report(json_path: str)
            Loads the json report from the given path.
        
        - generate_json_report(project_path: str)
            Generates the json report for the given project path.

        - complete_json_report()
            Completes the json report by adding the chunks to the files.
        
        - read_files_from_project_tree()
            Reads the files from the project tree.

        - save_response_for_file(filename: str, response: str, gid: int)
            Saves the response for the given file, in the given path.

        - from_filename_to_lang(filename: str)
            Infers the language from the filename.

        - chunk_document(filename_full_path: str, code: str, chunk_size: int, chunk_overlap: int = 0)
            Chunks the given document into the given chunk size, with the given overlap.

        - get_responses(responses_dir_path: str)
            Returns an iterator for the responses directory.
    """

    def __init__(self, json_path: str = None) -> None:
        self.py_files_paths = []
        self.json = None

        if json_path is not None:
            self.load_json_report(json_path)

    @staticmethod
    def save_response_for_file(filename: str, response: str, gid: int): # return the response in json format
        """
            This function is supposed to save the response of the model for a given file. 
            As a json file, following the format:

            filename_response.json

            Assuming the filename is a path, it will take the last part of the path, 
            and use it as the filename for the response.
        """

        output = f"{OUTPUTS_PATH}/" + filename.split("/")[-1].split(".")[0] + "_response.json"

        with open(output, "w") as f:
            f.write(response)

        with open(output, 'w') as f:
            res = json.loads(response)
            res["gid"] = gid
            json.dump(res, f, indent=4)

    @staticmethod
    def from_filename_to_lang(filename: str):
        """
            This function is supposed to take the filename and infer the language by taking the last part of the name
            and then return the Language it corresponds to if any (in the dict of supported LangChain languages)
            If it does not find it, it will return None

            Args:
            ----------
            filename: str
                The filename to infer the language from
            
            Returns:
            ----------
            Language
                The language that corresponds to the filename, if any.
        """
        return Language.PYTHON

    @staticmethod
    def chunk_document(filename_full_path: str, code: str, chunk_size: int, chunk_overlap: int = 0) -> List[Document]:
        """
            This function chunks a given block of code taking into account the semantic categories given in a language
            by considering it's syntax, from it recursively tries to divide each chunk into one or many of the desired
            chunk size, this does not guarantee that they all have the same size, but they should be close.
            Also considers the chunk overlap, which allows to have a bit of the previous information available.

            Args:
            ----------
            filename_full_path: str
                The full path to the file, including the filename and extension.
            code: str
                The code to chunk.
            chunk_size: int
                The size of the chunks to create.
            chunk_overlap: int
                The overlap between chunks.
            
            Returns:
            ----------
            List[Document]
                The list of documents created from the chunking.
        """

        filename = filename_full_path.split("/")[-1]
        lang = FileHandler.from_filename_to_lang(filename)
        python_splitter = RecursiveCharacterTextSplitter.from_language(chunk_size=chunk_size,
                                                                       chunk_overlap=chunk_overlap,
                                                                       language=lang, )
        docs = python_splitter.create_documents([code])
        return docs


    def get_responses(self, responses_dir_path: str):
        """
            This function returns an iterator which allows reading file by file inside the responses directory.
            This is useful for aboiding loading all the responses into memory at once, saving memory.

            Args:
            ----------
            responses_dir_path: str
                The path to the responses directory.
            
            Returns:
            ----------
            Iterator
                The iterator for the responses directory.
        """
        responses = {}
        for file in os.listdir(responses_dir_path):
            with open(responses_dir_path + file, "r") as f:
                jdir = json.load(f)
                responses[jdir["gid"]] = jdir
        return responses

    def load_file(self, file_path: str):
        """
            This function loads a file from the given path and returns it's contents.
        """
        with open(file_path, "r") as f:
            return f.read()


def main():
    dh = FileHandler()
    dh.generate_json_report(f"{PROJECTS_PATH}/Arquitectura")
    dh.read_files_from_project_tree()
    dh.complete_json_report()





if __name__ == "__main__":
    main()
