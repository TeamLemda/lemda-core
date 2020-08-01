from flask_restx import fields
from api import api

code = api.model("Blocks Code",{
    "code": fields.String(description="Name of the object")
})

name = api.model("Name",{
    "name": fields.String(description="Name of the object")
})

meta = api.model("Meta", {
	"ledma_api_version": fields.Float(description="The version of the Lemda API"),
	"name": fields.String(description="The name of the problem"),
})

question_source = api.model("Question Source", {
    "meta": fields.Nested(meta, description="Question metadata"),
    "generators": fields.Raw(description="The generator blocks of the question"),
    "checks": fields.Raw(description="The check blocks of the question"),
    "view": fields.Raw(description="The view blocks of the question"),
})

block = api.model("Block", {
    "name": fields.String(description="The name of the block"),
    "arguments": fields.Raw(description="List of arguments required for the block"),
    "documentation": fields.String(description="Block documentation"),
})

question = api.model("Question", {
    "meta": fields.Nested(meta, description="Question metadata"),
    "view": fields.Raw(description="The view blocks of the question"),
})

answer = api.model("Answer", {
    "view": fields.Raw(description="The answers")
})