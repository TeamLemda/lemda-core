from flask_restx import fields
from api import api

meta = api.model("Meta", {
	"ledma_api_version": fields.Float(description="The version of the Lemda API"),
	"name": fields.String(description="The name of the problem"),
})

block = api.model("Block", {
	"name": fields.String(description="The name of the block"),
	"arguments": fields.Raw(description="The arguments")
})

block_wild = fields.Wildcard(fields.Nested(block))
blocks = api.model("Blocks", {
	"*": block_wild
})

question_source = api.model("Question Source", {
    "meta": fields.Nested(meta, description="The name of the question"),
    "generators": fields.Nested(blocks, description="The generator blocks of the question"),
    "checks": fields.Nested(blocks, description="The check blocks of the question"),
    "view": fields.Nested(blocks, description="The view blocks of the question"),
})

question = api.model("Question", {
    "meta": fields.Nested(meta, description="The name of the question"),
    "view": fields.Nested(blocks, description="The view blocks of the question"),
})

answer = api.model("Question", {
    "meta": fields.Nested(meta, description="The name of the question"),
    "view": fields.Raw(description="The answers")
})