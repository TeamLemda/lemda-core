import logging
import traceback

from flask_restx import Api
import settings

log = logging.getLogger(__name__)

api = Api(version="0.1", title="Lemda API",
          description="Lemda Question API")


@api.errorhandler
def default_error_handler(e):
    message = "An unhandled exception occurred."
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {"message": message}, 500


@api.errorhandler(FileNotFoundError)
def file_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {"message": "The requested file was not found."}, 404

@api.errorhandler(RuntimeError)
def runtime_error_handler(e):
    log.warning(traceback.format_exc())
    return {"message": f"RuntimeError: {e}"}, 404