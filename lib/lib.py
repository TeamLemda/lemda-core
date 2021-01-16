import os
import json
import collections
import inspect

import random
import tokenize
import ast
import re
from io import StringIO

import sympy
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor
from sympy.polys import Poly

def to_latex(s):
    return latex(s).replace("{", "{{").replace("}", "}}")

def toProperFormula(s):
    """
    Given formula string, returns a modified formula with missing 
    multiplication symbols and grouping symbols [],{} replaced by parentheses.

    Only primitive error checking for mismatched grouping symbols is shown in 
    this recipe.

    author: ernesto.adorio@gmail.com, ernie@extremecomputing.org
    """

    f          = StringIO(s)
    
    # Make variables mutable to child function.
    formula    = [""]
    prevtoken  = [""]
    prevsymbol = [""]
    closers    = []
    
    def handle_token(type, token, t1, t2, line):
        (srow, scol) = t1
        (erow, ecol) = t2
        token  = str(token)
        symbol = tokenize.tok_name[type]
         
        if symbol == "OP":
            if token == ")":
                if  closers.pop() != "(":  raise SyntaxError('Error: "' +line[:ecol] + '" unbalanced ).')
            elif token == "]":
                if closers.pop() != "[":   raise SyntaxError('Error: "' +line[:ecol] + '" unbalanced ].')
                token = ")"
            elif token == "}":
                if closers.pop() != "{":   raise SyntaxError('Error: "' +line[:ecol] + '" unbalanced }.')
                token = ")"
            elif token in ["(", "[", "{"]:
                closers.append(token)
                if prevtoken[0] == ")" or prevsymbol[0] == "NUMBER":
                   formula[0] += "*"
                token = "("
        elif symbol in ["NAME", "NUMBER"]:
            if prevtoken[0] == ")" or prevsymbol[0] in ["NAME", "NUMBER"]:
                formula[0] += "*"

        formula[0]    += token
        prevtoken[0]  =  token
        prevsymbol[0] =  symbol


    for token in tokenize.generate_tokens(f.readline):
        handle_token(token[0], token[1], token[2], token[3], token[4])
    return formula[0]


def validate_function(response, variable, **state):
    if not response or not isinstance(response, str):
        ret = False
    else:
        try:
            response = toProperFormula(response)
            whitelist = (ast.Expression, ast.Call,
            ast.Name, ast.Load, ast.BinOp,
            ast.UnaryOp, ast.unaryop, ast.operator,
            ast.cmpop, ast.Num)

            tree = ast.parse(response, mode="eval")
            nodesAreValid = [isinstance(node, whitelist) for node in ast.walk(tree)]
            ret = all(nodesAreValid)
        except (SyntaxError, tokenize.TokenError) as e:
            ret = False
        if ret:
            fun = parse_expr(response, transformations=standard_transformations + (implicit_multiplication, convert_xor))
            if len(fun.free_symbols) != 0 and fun.free_symbols != {Symbol(variable)}:
                ret = False
        return ret


def validate_polynomial(response, variable, **state):
    if not response or not isinstance(response, str):
        raise BlockError("Invalid input")
    for c in response:
        if c not in "1234567890^+-/ ().*"+variable:
            raise BlockError(f"Invalid character {c}")
    return True

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

def describe_function(name, value):
    return {
        "name": remove_prefix(name,("lemda_block_")),
        "arguments": [a for a in inspect.getfullargspec(value).args if a != "seed"],
        "documentation": value.__doc__ or ""
    }


class Feedback(dict):
    def __init__(self, output, display, feedback, grade):
        dict.__init__(self, display=display, feedback=feedback, grade=grade)
        self.__dict__ = {
            "display": self["display"], 
            "feedback": self["feedback"], 
            "grade": self["grade"]
        }
        self.output = output

    def __str__(self):
        return str(self.display)

    def __repr__(self):
        return str({"display":self.display, "feedback":self.feedback, "grade":self.grade})

    def __iter__(self):
        print('Heres!!!!')
        for key in ['display', 'feedback', 'grade']:
            yield (key, getattr(self, key))

class BlockError(RuntimeError):
    pass

def format_list(arguments, **kwargs):
    """
    Using format strings, fills in a block's arguments values.
    """
    output = []
    for arg in arguments:
        if isinstance(arg, str):
            output.append(format_params(arg, **kwargs))
        elif isinstance(arg, dict) and not isinstance(arg, Feedback):
            output.append(format_dict(arg, **kwargs))
        elif isinstance(arg, list):
            output.append(format_list(arg, **kwargs))
    return output


def format_dict(arguments, **kwargs):
    """
    Using format strings, fills in a block's arguments values.
    """
    for arg_name, arg in arguments.items():
        if isinstance(arg, str):
            arguments[arg_name] = format_params(arg, **kwargs)
        elif isinstance(arg, dict) and not isinstance(arg, Feedback):
            arguments[arg_name] = format_dict(arg, **kwargs)
        elif isinstance(arg, list):
            arguments[arg_name] = format_list(arg, **kwargs)
    return arguments

def format_params(string, **dicts):
    """ Cheat to change string which only contain a reference to their object and not string reper """
    if len(string) < 3:
        o = string
    
    elif string[0] != "{" or  string[-1] != "}"  or string.count("{") != 1 or string.count("}") != 1:
        o = format_params_nonobj(string, **dicts)
    else:
        path = string[1:-1].split(".")
        curr = dicts
        while len(path) > 0:
            curr = curr[path.pop(0)]
        if isinstance(curr, Feedback):
            curr = curr.output
        o = curr
    return o

def format_params_nonobj(string, **dicts):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self
    def to_attrdict(dicts):
        attrdicts = {}
        for k, v in dicts.items():
            if isinstance(v, dict) and not isinstance(v, Feedback):
                attrdicts[k] = to_attrdict(v)
            else:
                attrdicts[k] = v
        return AttrDict(attrdicts)
    return string.format(string, **to_attrdict(dicts))

def list_files(folder, ext=None):
    """
    List file names without extension in a folder
    """
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if ext:
        files = [f for f in files if f.endswith("." + ext)]
    return [c for c in [".".join(f.split(".")[:-1]) for f in files] if c != ""]