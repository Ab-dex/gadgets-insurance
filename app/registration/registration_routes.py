#
# Blueprint: Registration
#
# >> Make sure to import bp as the correct blueprint <<
#
from app.registration import bp

from flask import request, url_for, current_app, jsonify, abort
from marshmallow import ValidationError
from app.schemas import UserRegistrationSchema, UserLoginSchema
from app.models import User
from sqlalchemy.exc import SQLAlchemyError
from app.registration import registration_service

#
# Register a new user
#
@bp.post('/auth/register')
def create_user():
    try:
        userinfo = request.get_json()

        if not userinfo:
            abort(400, description="All fields are required.")

        # Verify Username
        user = UserRegistrationSchema().load(userinfo)
        user_data = registration_service.registerUser(user, userinfo.get('password'))

        
        return jsonify({"data": user_data, "success": False, "message": "Account Created Successfully!"}), 201

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400


#
# Login a user
#
@bp.post('/auth/login')
def login_user():
    try:
        userinfo = request.get_json()

        # Verify Username
        user = UserLoginSchema().load(userinfo)

        token = registration_service.loginUser(user)
        
        return jsonify({"data": token, "success": False, "message": "Login Successful!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400

