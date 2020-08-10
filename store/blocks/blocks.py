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

def lemda_block_is_inflection(point, **state):
    is_inflection = (float(point)%pi) < 0.1
    return lib.Feedback(
        output=is_inflection,
        display=str(is_inflection),
        feedback="Right" if is_inflection else "Wrong",
        grade=100 if is_inflection else 0
    )

def lemda_block_do_latex(latex, **state):
    output = process_sympy(latex).doit()
    return lib.Feedback(output=output, display=lib.to_latex(output), feedback="", grade=None)

def lemda_block_generate_polynomial(degree, variable, minimum, maximum, seed, **state):
    random.seed(seed)
    coeff = [random.randint(int(minimum), int(maximum)) for _ in range(int(degree)+1)]
    p = Poly(coeff, sympy.Symbol(variable)).as_expr()
    return lib.Feedback(output=p, display=lib.to_latex(p), feedback="", grade=None)


def lemda_block_generate_number(minimum, maximum, seed, **state):
    random.seed(seed)
    number = random.randint(int(minimum), int(maximum))
    return lib.Feedback(output=number, display=str(number), feedback="", grade=None)

def lemda_block_parse_function(function, variable, **state):
    if not lib.validate_function(function, variable):
        raise lib.BlockError("Invalid function!")
    function = parse_expr(function, transformations=standard_transformations + (implicit_multiplication, convert_xor))
    return lib.Feedback(output=function, display=lib.to_latex(function), feedback="", grade=None)

def lemda_block_parse_polynomial(response, variable, **state):
    if not lib.validate_polynomial(response, variable):
        raise lib.BlockError("Invalid function!")
    p = None
    try:
        p = Poly(parse_expr(response, transformations=standard_transformations + (implicit_multiplication, convert_xor)), Symbol(variable))
    except SyntaxError:
        raise lib.BlockError("Invalid function!")
    output = p.as_expr()
    return lib.Feedback(output=output, display=lib.to_latex(output), feedback="", grade=None)

def lemda_block_differentiate(function, **state):
    """
    Calculates the derivative of a function.
    """
    diff = function.diff()
    return lib.Feedback(output=diff, display=lib.to_latex(diff), feedback="", grade=None)

def lemda_block_polynomials_are_equal(a, b, feedback_correct, feedback_incorrect, **state):
    value = False
    feedback = feedback_incorrect
    if a == b:
        value = True
        feedback = feedback_correct
    grade=(100 if value else 0)
    return lib.Feedback(output=value, display=f"%{grade}", feedback=feedback, grade=grade)

def lemda_block_limit_is(function, variable, limit_val, feedback_correct, feedback_incorrect, **state):
    value = False
    lim = limit(function,sympy.Symbol(variable),oo)
    feedback = feedback_incorrect + f", limit was {lim}"
    if lim == limit_val:
        value = True
        feedback = feedback_correct
    grade=(100 if value else 0)
    return lib.Feedback(output=value, display=f"%{grade}", feedback=feedback, grade=grade)
