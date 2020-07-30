import logging

from flask import request
from flask_restx import Resource

from store import QuestionStore
from store import BlockStore

from api import api
from api.serializers import question_source, block, name

log = logging.getLogger(__name__)

ns = api.namespace("curate", description="Operations related to question and block curation")


@ns.route("/blocks")
class BlocksList(Resource):

    @ns.doc("list_blocks")
    @ns.marshal_list_with(name)
    def get(self):
        """
        Returns list of blocks.
        """
        print(BlockStore.list_blocks())
        return BlockStore.list_blocks()


@ns.route("/blocks/<string:name>")
@ns.response(404, "Block not found.")
class Block(Resource):

    @ns.doc("get_block")
    @ns.marshal_with(block)
    def get(self, name):
        """
        Gets a block by name.
        """
        return BlockStore.get_block(name)

@ns.route("/questions")
class QuestionsList(Resource):

    @ns.doc("list_questions")
    @ns.marshal_list_with(name)
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


@ns.route("/questions/<string:name>")
@ns.response(404, "Question not found.")
class Question(Resource):

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
