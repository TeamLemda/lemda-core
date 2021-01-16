import lib
from pprint import pprint
from store import BlockStore

class Question():

    def __init__(self, question, **state):
        """
        Load code from file and generate.
        """
        self.__meta = question["meta"]
        self.__question = question
        self.__state = state
        self.__checks = {key:lib.Feedback(None, "", "", None) for key in question["checks"].keys()}
        self.__view = {}
        self.__generators = Blocks("generators", self.__question["generators"]).run(**self.__state)["output"]
    
    def check(self, answer):
        """
        Check answers based on view.
        """
        ret = True
        checks = Blocks("checks", self.__question["checks"]).run(
            answer=answer["answer"],
            generators=self.__generators,
            **self.__state
        )
        if not checks["status"]:
            ret = False
        for k, v in checks["output"].items():
            self.__checks[k] = v
        return ret

    def check_view(self):
        """
        Show only the checks.
        """
        view = {
            "checks": lib.format_dict(self.__checks, generators=self.__generators, state=self.__state),
        }
        return view

    def view(self):
        """
        Show the question.
        """
        view = {
            "meta": self.__meta,
            "generators": lib.format_dict(self.__generators, state=self.__state),
            "checks": lib.format_dict(self.__checks, generators=self.__generators, state=self.__state),
            "view": self.__question["view"]
        }
        return view
            

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
                output[block_output_name] = lib.Feedback(output=None, display=None, feedback=f"Missing field {str(e)}", grade=None)
                success = False
                break
            try:
                output[block_output_name] = BlockStore.get_code(block["name"])(**{**arguments, **kwargs})
            except lib.BlockError as e:
                output[block_output_name] = lib.Feedback(output=None, display=None, feedback=str(e), grade=None)
                success = False
                break
            if not isinstance(output[block_output_name],lib.Feedback):
                output[block_output_name] = lib.Feedback(output=output[block_output_name], display=output[block_output_name], feedback="", grade=None)
        return {"status": success, "output": output}
