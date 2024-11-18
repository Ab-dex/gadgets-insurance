from flask import Blueprint, jsonify, request

from app.middlewares import errors_bp


# 400 Bad Request Error Handler
@errors_bp.app_errorhandler(400)
def bad_request_error(error):
    response = {
        "error": "Bad Request",
        "message": str(error.description) if error.description else "Invalid request data."
    }
    return jsonify(response), 400

# 404 Not Found Error Handler
@errors_bp.app_errorhandler(404)
def not_found_error(error):
    response = {
        "error": "Not Found",
        "message": str(error.description) if error.description else "The requested resource could not be found."
    }
    return jsonify(response), 404

# 401 Unauthorized Error Handler
@errors_bp.app_errorhandler(401)
def unauthorized_error(error):
    response = {
        "error": "Unauthorized",
        "message": "You must be authenticated to access this resource."
    }
    return jsonify(response), 401

@errors_bp.app_errorhandler(403)
def unauthorized_error(error):
    response = {
        "error": "Forbidden",
        "message": str(error.description) if error.description else "You are not allowed to make this request"
    }
    return jsonify(response), 403


@errors_bp.app_errorhandler(409)
def unauthorized_error(error):
    response = {
        "error": "Multiple Distributors Request",
        "message": str(error.description) if error.description else "You can't perform this action"
    }
    return jsonify(response), 409

# 415 Unsupported Media Type Error Handler
@errors_bp.app_errorhandler(415)
def unsupported_media_type_error(error):
    response = {
        "error": "Unsupported Media Type",
        "message": "Invalid Content-Type. Expected 'application/json'."
    }
    return jsonify(response), 415

# 500 Internal Server Error Handler
@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }
    return jsonify(response), 500

# Custom Error Handler (For example, when user is not found)
@errors_bp.app_errorhandler(Exception)
def general_error(error):
    response = {
        "error": "Error",
        "message": str(error)
    }
    return jsonify(response), 500

# Example to catch custom validation errors
class ValidationError(Exception):
    pass
