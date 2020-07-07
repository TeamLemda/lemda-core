import logging.config
import os
from flask import Flask, Blueprint

import settings
from api.endpoints.curate import ns as curate_namespace
#from lemda.api.endpoints.test import ns as test_namespace
from api.endpoints.questions import ns as questions_namespace
from api import api

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "logging.conf"))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

def configure_app(flask_app):
    """
    Loads settigns from settings file and sets configuration accordingly.
    """
    flask_app.config["SERVER_NAME"] = settings.FLASK_SERVER_NAME
    flask_app.config["SWAGGER_UI_DOC_EXPANSION"] = settings.RESTX_SWAGGER_UI_DOC_EXPANSION
    flask_app.config["RESTX_VALIDATE"] = settings.RESTX_VALIDATE
    flask_app.config["RESTX_MASK_SWAGGER"] = settings.RESTX_MASK_SWAGGER
    flask_app.config["ERROR_404_HELP"] = settings.RESTX_ERROR_404_HELP

def initialize_app(flask_app):
    """
    Builds up the API.
    """
    configure_app(flask_app)

    blueprint = Blueprint("api", __name__, url_prefix="/api")
    api.init_app(blueprint)
    api.add_namespace(curate_namespace)
    #api.add_namespace(test_namespace)
    #api.add_namespace(questions_namespace)
    flask_app.register_blueprint(blueprint)

def main():
    """
    Runs the app.
    """
    initialize_app(app)
    log.info(">>>>> Starting development server at http://{}/api/ <<<<<".format(app.config["SERVER_NAME"]))
    app.run(debug=settings.FLASK_DEBUG)

if __name__ == "__main__":
    main()
