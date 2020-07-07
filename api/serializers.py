from flask_restx import fields
from api import api

question = api.model("Question", {
    "name": fields.String(readOnly=True, description="The name of the question"),
    "fields": fields.Raw(readOnly=True, description="The fields of the question"),
    "view": fields.String(readOnly=True, description="The view of the question"),
})

question_source = api.model("Question Source", {
    "name": fields.String(required=True,  description="The name of a question"),
    "content": fields.Raw(required=True, description="The source code of a question"),
})

answer = api.model("Answer", {
    "response": fields.Raw(required=True, description="An answer to a question"),
})

feedback = api.model("Feedback", {
    "grade": fields.Integer(description="The question grade"),
    "feedback": fields.List(fields.String(description="The question feedbacks"))
})
