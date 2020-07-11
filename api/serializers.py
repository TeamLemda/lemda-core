from flask_restx import fields
from api import api

meta = api.model("Meta", {
	"ledma_api_version": fields.Float(description="The version of the Lemda API"),
	"name": fields.String(description="The name of the problem"),
})

question_source = api.model("Question Source", {
    "meta": fields.Nested(meta, description="The name of the question"),
    "generators": fields.Raw(description="The generator blocks of the question"),
    "checks": fields.Raw(description="The check blocks of the question"),
    "view": fields.Raw(description="The view blocks of the question"),
})

question = api.model("Question", {
    "meta": fields.Nested(meta, description="The name of the question"),
    "view": fields.Raw(description="The view blocks of the question"),
})

answer = api.model("Question", {
    "meta": fields.Nested(meta, description="The name of the question"),
    "view": fields.Raw(description="The answers")
})