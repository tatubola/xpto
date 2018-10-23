"""Module with Error Messages."""
# System imports

# Third-party imports
from flask import request, jsonify

# Local source tree imports
from run import app


@app.errorhandler(404)
def page_not_found(error):
    message = {
        "status": 404,
        "message": "The requested resource was not found",
        "requested path": request.path,
        "error": error
    }
    return jsonify(message), 404


@app.errorhandler(500)
def internal_server_error(error):
    message = {
        "status": 500,
        "message": "Server Error",
        "error": error
    }

    return jsonify(message), 500


@app.errorhandler(Exception)
def unhandled_exception(error):
    message = {
        "status": 500,
        "message": "Unhandled Exception",
        "error": error
    }

    return jsonify(message), 500
