import os
import importlib
import json
import inspect

import lib


class BlockStore():
    """
    Handels access to blocks from the lib
    """
   
    # Path to where blocks are, should probably be relative.
    BLOCKS_FOLDER = "store/blocks/"

    @staticmethod
    def __parse_path(path):
        return tuple(path.split("."))

    @staticmethod
    def __get_module(file):
        return importlib.import_module("..blocks."+file, __name__)

    @staticmethod
    def __get_code(lib, name):
        return getattr(BlockStore.__get_module(lib), "lemda_block_" + name)

    @staticmethod
    def list_blocks():
        """
        Get a list of all block
        """
        blocks = []
        for file in lib.list_files(BlockStore.BLOCKS_FOLDER):
            module = BlockStore.__get_module(file)
            for f in inspect.getmembers(module):
                if not f[0].startswith("lemda_block_"):
                    continue
                blocks.append({"name": lib.remove_prefix(f[0],("lemda_block_"))})
        return blocks

    @staticmethod
    def get_block(path):
        """
        Get information on a specific block
        """
        try:
            module, name = BlockStore.__parse_path(path)
            return lib.describe_function(name, BlockStore.__get_code(module, name))
        except AttributeError:
            raise FileNotFoundError("No such block")

    @staticmethod
    def get_code(path):
        """
        Get code of specific block
        """
        return BlockStore.__get_code(*BlockStore.__parse_path(path))


class QuestionStore():
    """
    Handels access to questions on disk.
    """

    # Path to where questions are, should probably be relative.
    QUESTIONS_FOLDER = "store/questions/"

    @staticmethod
    def list_questions():
        """
        Get a list of all questions
        """
        return [{"name": n} for n in lib.list_files(QuestionStore.QUESTIONS_FOLDER)]

    @staticmethod
    def get_question(question_name):
        """
        Get the JSON of a specefied question
        """
        return json.load(open(os.path.join(QuestionStore.QUESTIONS_FOLDER, question_name + ".json")))

    @staticmethod
    def save_question(question_name, question):
        """
        Update the content of a question
        """
        json.dump(question, open(os.path.join(QuestionStore.QUESTIONS_FOLDER, question_name + ".json"),"w"))

    @staticmethod
    def delete_question(question_name):
        """
        Delete a question
        """
        os.remove(os.path.join(QuestionStore.QUESTIONS_FOLDER, question_name + ".json"))