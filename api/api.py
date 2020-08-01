import logging
import traceback

import flask
from flask_restx import Api
import settings

log = logging.getLogger(__name__)

@property
def specs_url(self):
    """Fixes issue where swagger-ui makes a call to swagger.json over HTTP.
       This can ONLY be used on servers that actually use HTTPS.  On servers that use HTTP,
       this code should not be used at all.
    """
    return flask.url_for(self.endpoint('specs'), _external=False)

@property
def base_url(self):
    """Fixes issue where swagger-ui makes a call to swagger.json over HTTP.
       This can ONLY be used on servers that actually use HTTPS.  On servers that use HTTP,
       this code should not be used at all.
    """
    return flask.url_for(self.endpoint("root"), _external=False)

Api.specs_url = specs_url
Api.base_url = base_url
api = Api(version="0.1", title="Lemda API",
          description="Lemda Question API")



def create_message(content):
	return {
	    "meta": {
	        "ledma_api_version": 0.1,
	        "name": "limit"
	    },
	    "view": {
	        "view": {
	            "name": "view.html",
	            "arguments": {
	                "content": content,
	                "grade": None
	            }
	        }
	    }
	}

@api.errorhandler
def default_error_handler(e):
    message = "An unhandled exception occurred."
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return create_message(message), 500


@api.errorhandler(FileNotFoundError)
def file_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return create_message("The requested file was not found."), 404