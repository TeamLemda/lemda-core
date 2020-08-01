import random
import tokenize
import ast
import re
from io import StringIO
    
import sympy
from latex2sympy.process_latex import process_sympy
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor
from sympy.polys import Poly


import lib

def lemda_block_parse_int(inp, **state):
    return int(inp)

def lemda_block_do_sympy(sympy, **state):
    return eval(sympy)

def lemda_block_do_latex(latex, **state):
    return process_sympy(latex).doit()

def lemda_block_parse_point(point, **state):
    return float(point)

def lemda_block_is_inflection(point, **state):
    return (float(point)%pi) < 0.1

def lemda_block_poly_to_expr(object, **state):
    return object.as_expr()

def lemda_block_poly_to_latex(object, **state):
    return lemda_block_to_latex(object.as_expr())

def lemda_block_to_latex(object, **state):
    a = latex(object).replace("{", "{{").replace("}", "}}")
    return a

def lemda_block_generate_polynomial(degree, variable, minimum, maximum, seed, **state):
    random.seed(seed)
    coeff = [random.randint(int(minimum), int(maximum)) for _ in range(int(degree)+1)]
    return Poly(coeff, sympy.Symbol(variable))


def lemda_block_generate_number(minimum, maximum, seed, **state):
    random.seed(seed)
    return random.randint(int(minimum), int(maximum))


def lemda_block_validate_polynomial(response, variable, **state):
    if not response or not isinstance(response, str):
        raise lib.BlockError("Invalid input")
    for c in response:
        if c not in "1234567890^+-/ ().*"+variable:
            raise lib.BlockError(f"Invalid character {c}")
    return True

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


def lemda_block_validate_function(response, variable, **state):
    if not response or not isinstance(response, str):
        raise lib.BlockError("Invalid input")

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

def lemda_block_parse_function(function, variable, **state):
    if not lemda_block_validate_function(function, variable):
        raise lib.BlockError("Invalid function!")
    return parse_expr(function, transformations=standard_transformations + (implicit_multiplication, convert_xor))


def lemda_block_parse_polynomial(response, variable, **state):
    if not lemda_block_validate_polynomial(response, variable):
        raise lib.BlockError("Invalid function!")
    p = None
    try:
        p = Poly(parse_expr(response, transformations=standard_transformations + (implicit_multiplication, convert_xor)), Symbol(variable))
    except SyntaxError:
        raise lib.BlockError("Invalid function!")
    return p.as_expr()

def lemda_block_differentiate(function, **state):
    """
    Calculates the derivative of a function.
    """
    return function.diff()

def lemda_block_polynomials_are_equal(a, b, feedback_correct, feedback_incorrect, **state):
    value = False
    feedback = feedback_incorrect
    if a == b:
        value = True
        feedback = feedback_correct
    return lib.Feedback(value, feedback)

def lemda_block_grade_from_bool(is_correct, **state):
    grade = 100 if is_correct else 0
    return grade

def lemda_block_limit_is(function, variable, limit_val, feedback_correct, feedback_incorrect, **state):
    value = False
    lim = limit(function,sympy.Symbol(variable),oo)
    feedback = feedback_incorrect + f", limit was {lim}"
    if lim == limit_val:
        value = True
        feedback = feedback_correct
    return lib.Feedback(value, feedback)