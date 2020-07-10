import os
import json

import lib


QUESTIONS_FOLDER = "store/questions/"

class QuestionStore():
	"""
	Handels access to questions on disk.
	"""

	@staticmethod
	def list_questions():
		"""
		Get a list of all questions
		"""
		return [QuestionStore.get_question(name) for name in lib.list_files(QUESTIONS_FOLDER)]

	@staticmethod
	def get_question(question_name):
		"""
		Get the JSON of a specefied question
		"""
		return json.load(open(os.path.join(QUESTIONS_FOLDER, question_name + ".json")))

	@staticmethod
	def save_question(question_name, question):
		"""
		Update the content of a question
		"""
		json.dump(question, open(os.path.join(QUESTIONS_FOLDER, question_name + ".json"),"w"))

	@staticmethod
	def delete_question(question_name):
		"""
		Delete a question
		"""
		os.remove(os.path.join(QUESTIONS_FOLDER, question_name + ".json"))