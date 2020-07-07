import logging

from flask import request
from flask_restx import Resource

from store import QuestionStore
from lemda import Question

from api import api
from api.serializers import question, answer, feedback

log = logging.getLogger(__name__)

ns = api.namespace("questions", description="Operations related to question solving")


@ns.route("/")
class QuestionsList(Resource):

    @ns.doc("list_questions")
    @ns.marshal_list_with(question)
    def get(self):
        """
        Returns list of questions.
        """
        ret = [{"name": name, **Question(q).get_view()} for name, q in QuestionStore.list_questions()]
        print(ret)
        return ret


@ns.route("/<string:name>/<int:seed>")
@ns.response(404, "Question not found.")
class Questions(Resource):

    @ns.doc("get_question")
    @ns.marshal_with(question)
    def get(self, name, seed):
        """
        Gets a question by name.
        """
        return {"name": name, **Question(QuestionStore.get_question(name), seed=seed).get_view()}

    @ns.doc("check_answer")
    @ns.expect(answer)
    @ns.marshal_with(feedback)
    def put(self, name, seed):
        """
        Checks a question, by name and answer.
        """
        return Question(QuestionStore.get_question(name), seed=seed).get_checked(api.payload["response"])