import logging

from flask import request
from flask_restx import Resource

from store import QuestionStore
from lemda import Question

from api import api
from api.serializers import question, answer, checked

log = logging.getLogger(__name__)

ns = api.namespace("questions", description="Operations related to question solving")


@ns.route("/<int:seed>")
class QuestionsList(Resource):

    @ns.doc("list_questions")
    @ns.marshal_list_with(question)
    def get(self, seed):
        """
        Returns list of questions.
        """
        ret = [Question(QuestionStore.get_question(q["name"]), seed=seed).view() for q in QuestionStore.list_questions()]
        return ret


@ns.route("/<int:seed>/<string:name>")
@ns.response(404, "Question not found.")
class Questions(Resource):

    @ns.doc("get_question")
    @ns.marshal_with(question)
    def get(self, name, seed):
        """
        Gets a question by name.
        """
        v = Question(QuestionStore.get_question(name), seed=seed).view()
        return v

    @ns.doc("check_answer")
    @ns.expect(answer)
    @ns.marshal_with(checked)
    def put(self, name, seed):
        """
        Checks a question, by name and answer.
        """
        q = Question(QuestionStore.get_question(name), seed=seed)
        check = q.check(api.payload)
        view = q.view()
        if not check:
            return view, 400
        return view