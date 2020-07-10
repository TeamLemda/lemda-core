import logging

from flask import request
from flask_restx import Resource

from store import QuestionStore

from api import api
from api.serializers import question_source

log = logging.getLogger(__name__)

ns = api.namespace("curate", description="Operations related to question curation")


@ns.route("/")
class QuestionsSourceList(Resource):

    @ns.doc("list_questions")
    @ns.marshal_list_with(question_source)
    def get(self):
        """
        Returns list of questions.
        """
        return QuestionStore.list_questions()

    @ns.doc("create_question")
    @ns.response(201, "Question successfully created.")
    @ns.expect(question_source)
    def post(self):
        """
        Creates a new question.
        """
        QuestionStore.save_question(api.payload["meta"]["name"], api.payload)
        return None, 201


@ns.route("/<string:name>")
@ns.response(404, "Question not found.")
class QuestionSource(Resource):

    @ns.doc("get_question")
    @ns.marshal_with(question_source)
    def get(self, name):
        """
        Gets a question by name.
        """
        return QuestionStore.get_question(name)

    @ns.doc("update_question")
    @ns.expect(question_source)
    @ns.response(204, "Question successfully updated.")
    def put(self, name):
        """
        Updates a question by name.
        """
        QuestionStore.save_question(api.payload["meta"]["name"], api.payload)
        return None, 204

    @ns.doc("delete_question")
    @ns.response(204, "Question successfully deleted.")
    def delete(self, name):
        """
        Deletes a question.
        """
        QuestionStore.delete_question(name)
        return None, 204
