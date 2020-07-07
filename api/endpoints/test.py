import logging

from lemda.api.api import api

log = logging.getLogger(__name__)

ns = api.namespace('test', description='Operations related to question testing')

# Does nothing for now...