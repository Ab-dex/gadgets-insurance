from flask_jwt_extended import get_jwt
from flask import jsonify

def is_admin(fn):
    """
    Decorator to check if the current user is an admin.
    """
    def wrapper(*args, **kwargs):
        # Get the claims from the current JWT token
        claims = get_jwt()
        # Check if the user has 'role' claim as 'admin'
        if claims.get("role") != "admin":
            return jsonify(message="You do not have permission to access this resource"), 403
        return fn(*args, **kwargs)
    return wrapper