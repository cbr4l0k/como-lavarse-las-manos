import os
from typing import List
from dotenv import load_dotenv
from langchain.text_splitter import (RecursiveCharacterTextSplitter, Language)
from langchain.schema.document import Document

#some important enviroment variables
load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")
GRAMMAR_PATH = os.getenv("GRAMMAR_PATH")
PROJECTS_PATH = os.getenv("PROJECTS_PATH")
OUTPUTS_PATH = os.getenv("OUTPUTS_PATH")


class DocumentHandler:

    def __init__(self):
        pass

    @staticmethod
    def save_response_for_file(filename: str, response: str):

        """
            This function is supposed to save the response of the model for a given file. 
            As a json file, following the format:

            filename_response.json

            Assuming the filename is a path, it will take the last part of the path, 
            and use it as the filename for the response.
        """

        output = OUTPUTS_PATH + filename.split("/")[-1].split(".")[0] + "_response.json"
        with open(output, "w") as f:
            f.write(response)


    @staticmethod
    def from_filename_to_lang(filename: str):
        """
        This function is supposed to take the filename and infer the language by taking the last part of the name
        and then return the Language it corresponds to if any (in the dict of supported LangChain languages)
        """
        return Language.PYTHON

    @staticmethod
    def chunk_document(filename: str, code: str, chunk_size: int, chunk_overlap: int = 0) -> List[Document]:
        """
        This function chunks a given block of code taking into account the semantic categories given in a language
        by considering it's syntax, from it recursively tries to divide each chunk into one or many of the desired
        chunk size, this does not guarantee that they all have the same size, but they should be close.

        Also considers the chunk overlap, which allows to have a bit of the previous information available.
        """

        lang = DocumentHandler.from_filename_to_lang(filename)
        python_splitter = RecursiveCharacterTextSplitter.from_language(chunk_size=chunk_size,
                                                                       chunk_overlap=chunk_overlap,
                                                                       language=lang,)
        docs = python_splitter.create_documents([code])
        return docs

    @staticmethod
    def read_files_from_project_tree(project_path: str):

        """
            Return an iterator which allows reading file by file inside the project tree.
        """
        pass

