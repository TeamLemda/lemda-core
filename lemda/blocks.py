import random

import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor
from sympy.polys import Poly

def generate_polynomial(degree, variable, minimum, maximum, seed, **state):
	random.seed(seed)
	coeff = [random.randint(minimum, maximum) for _ in range(degree+1)]
	return Poly(coeff, sympy.Symbol(variable))

def validate_polynomial(response, variable, **state):
	if not response or not isinstance(response, str):
		raise RuntimeError("Invalid input")
	for c in response:
		if c not in "1234567890^+-/ ()."+variable:
			raise RuntimeError(f"Invalid character {c}")
	return True

def parse_polynomial(response, variable, **state):
	return Poly(parse_expr(response, transformations=standard_transformations + (implicit_multiplication, convert_xor)))

def differentiate(function, **state):
	return function.diff()

def polynomials_are_equal(a, b, feedback_correct, feedback_incorrect, **state):
	value = False
	feedback = feedback_incorrect
	if a.coeffs() == b.coeffs():
		value = True
		feedback = feedback_correct
	return (value, feedback)

def grade_from_bool(field, **state):
	grade = 100 if field else 0
	return (grade, None)
