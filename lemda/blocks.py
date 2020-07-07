def generate_polynomial(degree, variable, **state):
	return "x^3 + 5"

def validate_polynomial(response, variable, **state):
	print(response)	
	if not response or "y" in response:
		raise RuntimeError("Invalid input")
	return True if response else False

def parse_polynomial(response, variable, **state):
	return response

def differentiate(function, **state):
	return "3x^2"

def algerbric_is_equal(a, b, feedback_correct, feedback_incorrect, **state):
	value = False
	feedback = feedback_incorrect
	if a == b:
		value = True
		feedback = feedback_correct
	return (value, feedback)

def grade_from_bool(field, **state):
	grade = 100 if field else 0
	return (grade, None)
