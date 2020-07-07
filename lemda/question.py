import unittest
import json

import lib
from . import blocks

def _question(question_code):
    """
    Does base parses of a question source
    """
    question_code = lib.replace_methods(blocks, "method", question_code)
    generators = question_code["generators"]
    fields = question_code["fields"]
    checks = question_code["checks"]
    view = question_code["view"]
    samples = None #question_code["samples"] @TODO enable samples...

    return generators, fields, checks, view, samples

class TestQuestion(unittest.TestCase):

    #@TODO add generic tests - grades sum to 100, all functions defined...
    #@TODO return response in a way it can be used in the API

    def __init__(self, question_source):
        generators, fields, checks, _, samples = _question(question_source)
        self.test_parameters(samples["test_parameters"], generators)
        self.test_parsed(samples["test_parsed"], fields)
        self.test_checks(samples["test_checks"], checks)

    def test_parameters(self, samples, generators):
        for sample in samples:
            test_generator = Generator(generators, **sample["state"])
            self.assertTrue(sample["parameters"] == test_generator.generate())

    def test_parsed(self, samples, fields):
        for sample in samples:
            test_parser = Parser(fields, **sample["state"])
            if "parsed" in sample:
                self.assertTrue(sample["parsed"] == test_parser.parse(sample["parameters"], sample["response"]))
            else:
                with self.assertRaises(RuntimeError):
                    test_parser.parse(sample["parameters"], sample["response"])


    def test_checks(self, samples, checks):
        for sample in samples:
            test_checker = Checker(checks, **sample["state"])
            self.assertTrue(sample["checked"] == test_checker.check(sample["parameters"], sample["parsed"]))


class Question():

    def __init__(self, question_source, **state):
        """
        All arguments are dictionaries of unparsed json (i.e. the two-top-level dicts are parsed and that's it)
        because the json references internal fields and functions.
        so 'generators':{'name' :{json}, 'name': {json}}
        """
        generators, self.__fields, checks, self.__view, _ = _question(question_source)
        if "seed" not in state:
            state["seed"] = 0
        self.__generator = Generator(generators, **state)
        self.__parser = Parser(self.__fields, **state)
        self.__checker = Checker(checks, **state)

        self.__parameters = None
        self.__parsed = None

        self.__generate()

    def __generate(self):
        self.__parameters = self.__generator.generate()
        
    def __parse(self, responses):
        self.__parsed = self.__parser.parse(self.__parameters, responses)

    def __check(self):
        self.__feedback = self.__checker.check(self.__parameters, self.__parsed)
    
    def get_checked(self, responses):
        self.__parse(responses)
        self.__check()
        return self.__feedback

    def get_view(self):
        fields = {}
        params = {}
        for k, v in self.__parameters.items():
            params[k] = str(v)
        for field_name, content in self.__fields.items():
            field = {} 
            parsed = lib.replace_parameters(content, parameters=params)
            field["type"] = parsed["type"]
            field["correct"] = parsed["correct"]
            fields[field_name] = field
        view = self.__view.format(**params)
        ret = {"fields": json.dumps(fields), "view": view}
        return ret
        


class Generator():

    def __init__(self, parameters, **state):
        self.__parameters = parameters
        self.__state = state

    def generate(self):
        parameters = {}
        for parameter_name, generator_json in self.__parameters.items():
            generator = lib.replace_parameters(generator_json, parameters=parameters)
            parameters[parameter_name] = generator["method"](**{**generator["arguments"], **self.__state})
        return parameters


class Parser():

    def __init__(self, fields, **state):
        self.__fields = fields
        self.__state = state

    def parse(self, parameters, responses):
        parsed = {}
        for field_name, validator_parser_json in self.__fields.items():
            validator_parser = lib.replace_parameters(validator_parser_json, parameters=parameters, parsed=parsed)
            validator = validator_parser["validator"]
            parser = validator_parser["parser"]
            response = responses[field_name] if field_name in responses else None
            if validator["method"](response, **{**validator["arguments"], **self.__state}):
                parsed[field_name] = parser["method"](response, **{**parser["arguments"], **self.__state})
            else:
                raise RuntimeError(f"Invalid input received for {field_name}")
        return parsed


class Checker():

    def __init__(self, checks, **state):
        self.__checks = checks
        self.__state = state
        self.__checked = None

    def check(self, parameters, parsed):
        checked = {}
        feedbacks = []
        grade = 0
        for check_name, checker_json in self.__checks.items():
            checker = lib.replace_parameters(checker_json, parameters=parameters, parsed=parsed, checked=checked)
            value, feedback = checker["method"](**{**checker["arguments"], **self.__state})
            checked[check_name] = value
            if feedback:
                feedbacks.append(feedback)
            if check_name == "grade":
                grade = value
        return {'grade': grade, 'feedback': feedbacks}
