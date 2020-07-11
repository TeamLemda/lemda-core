import unittest
import json
import importlib

import lib

class Question():

    def __init__(self, question, **state):
        """
        Load code from file and generate.
        """
        self.__meta = question["meta"]
        self.__question = question
        self.__state = state
        self.__checks = {key:lib.Feedback(None, "") for key in question["checks"].keys()}
        self.__view = {key:f"{{view.{key}}}" for key in question["view"].keys()}
        self.__generators = Blocks("generators", self.__question["generators"]).run(**self.__state)["output"]
    
    def check(self, answer):
        """
        Check answers based on view.
        """
        ret = True
        checks = Blocks("checks", self.__question["checks"]).run(
            view=answer["view"],
            generators=self.__generators,
            **self.__state
        )
        if not checks["status"]:
            ret = False
        for k, v in checks["output"].items():
            self.__checks[k] = v
        return ret

    def view(self):
        """
        Show the question.
        """
        return {
            "meta": self.__meta,
            "view": lib.format_dict(
                self.__question["view"],
                view=self.__view,
                checks=self.__checks,
                generators=self.__generators,
                state=self.__state
            )
        }
            

class Blocks():
    """
    Class representing a blocks chunk.
    """

    def __init__(self, name, blocks):
        """
        Init.
        """
        self.__name = name
        self.__blocks = blocks

    def __get_block(self, block_name):
        """
        Gets a block
        """
        lib, name = tuple(block_name.split("."))
        return getattr(importlib.import_module("..blocks."+lib, __name__), name)

    def run(self, **kwargs):
        """
        Runs all blocks in a block chunk.
        """
        success = True
        output = {}
        for block_output_name, block in self.__blocks.items():
            try:
                arguments = lib.format_dict(block["arguments"], **{self.__name: output, **kwargs})
            except KeyError as e:
                output[block_output_name] = lib.Feedback(None, f"Missing field {str(e)}")
                success = False
                break
            try:
                output[block_output_name] = self.__get_block(block["name"])(**{**arguments, **kwargs})
            except lib.BlockError as e:
                output[block_output_name] = lib.Feedback(None, str(e))
                success = False
                break
            if not isinstance(output[block_output_name],lib.Feedback):
                output[block_output_name] = lib.Feedback(output[block_output_name], "")
        return {"status": success, "output": output}
