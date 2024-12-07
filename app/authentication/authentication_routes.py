#
# Blueprint: Authentication
#
# >> Make sure to import bp as the correct blueprint <<
#
from app.authentication import bp

from flask import jsonify
from app import auth
from app.authentication import authentication_service as auth_service
from app.user import user_service
from flask import request, url_for, current_app, jsonify, abort
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from app.schemas import ProfileSchema, AgentRegistrationSchema, AgentLoginSchema, AgentOtpSchema, DistributorRegistrationSchema, InsuranceCompanyRegistrationSchema
#
# Generate a new API token
#

@bp.get('/test')
def test_auth():
    return jsonify({'message': 'Phonetheft api server works fine',})


# @bp.route('/auth/token')
# @auth.login_required
# def get_auth_token():
#     token = auth_service.generate_auth_token(600)
#     return jsonify({'token': token.decode('ascii'), 'duration': 600})

@bp.route('/auth/refresh')
@jwt_required(refresh=True)
def get_new_access_token():
    identity = get_jwt_identity()
    access_token, _ = auth_service.generate_auth_token(identity, True)
    return jsonify({'accessToken': access_token, 'success': True})


#
# Register a new distributor
#
@bp.post('/auth/distributor/register')
def register_dealer():
    try:
        distributorInfo = request.get_json()

        # Verify Email
        distributor = DistributorRegistrationSchema().load(distributorInfo)
        distributor_data = auth_service.registerDistributor(distributor, distributorInfo.get('password'))

        profile_schema = ProfileSchema()

        result = profile_schema.load(distributor_data['user'])

        profile_data = user_service.create_profile(result)

        
        return jsonify({"data": distributor_data, "success": True, "message": "Account Created Successfully!"}), 201

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400


#
# Onboard a new distributor
#
# @bp.post('/auth/onboarding')
# def onboarding():
#     try:
#         dealerInfo = request.get_json()

#         # Verify Email
#         dealer = DistributorRegistrationSchema().load(dealerInfo)
#         dealer_data = auth_service.registerDealer(dealer, dealerInfo.get('password'))

        
#         return jsonify({"data": dealer_data, "success": True, "message": "Account Created Successfully!"}), 201

#     except ValidationError as err:
#         current_app.logger.info(err.messages)
#         return jsonify({"errors": err.messages, "success": False}), 400


#
# Send Otp to email
#
@bp.post('/auth/send_otp')
def send_otp():
    try:
        userinfo = request.get_json()

        # Verify Email
        user = AgentOtpSchema().load(userinfo)
        user_data = auth_service.sendOtp(userinfo.get('email'))

        
        return jsonify({"data": user_data, "success": True, "message": "Account Created Successfully!"}), 201

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400


#
# Register a new agent
#
@bp.post('/auth/register')
def create_user():
    try:
        userinfo = request.get_json()

        if not userinfo:
            abort(400, description="All fields are required.")

        # Verify Credentials
        user = AgentRegistrationSchema().load(userinfo)
        user_data = auth_service.registerUser(user, userinfo.get('password'))

        profile_schema = ProfileSchema()

        result = profile_schema.load(user_data['user'])

        profile_data = user_service.create_profile(result)

        
        return jsonify({"data": user_data, "success": True, "message": "Account Created Successfully!"}), 201

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400


#
# Register a new admin
#
@bp.post('/auth/admin/register')
def register_admin():
    try:
        admininfo = request.get_json()

        if not admininfo:
            abort(400, description="All fields are required.")

        # Verify Username
        user = AgentRegistrationSchema().load(admininfo)
        user_data = auth_service.registerUser(user, admininfo.get('password'))

        
        return jsonify({"data": user_data, "success": True, "message": "Account Created Successfully!"}), 201

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
        user = AgentLoginSchema().load(userinfo)

        token = auth_service.loginUser(user)
        
        return jsonify({"data": token, "success": True, "message": "Login Successful!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400
    

#
# Register a new insurance company
#
@bp.post('/auth/insurance/register')
def register_insurance_company():
    try:
        # Get JSON data from the request body
        company_info = request.get_json()

        # Verify the input data using a Schema
        insurance_company = InsuranceCompanyRegistrationSchema().load(company_info)
        
        # Register the insurance company using the service layer
        company_data = auth_service.registerInsuranceCompany(insurance_company, company_info.get('password'))

        # Create a profile for the company
        profile_schema = ProfileSchema()
        result = profile_schema.load(company_data['user'])

        # Create the profile and associate it with the company
        profile_data = user_service.create_profile(result)

        # Return a successful response with the company data
        return jsonify({"data": company_data, "success": True, "message": "Insurance Company Registered Successfully!"}), 201

    except ValidationError as err:
        # Handle validation errors
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400

    except Exception as e:
        # Handle any unexpected errors
        current_app.logger.error(f"Error during registration: {str(e)}")
        return jsonify({"message": "An error occurred during registration.", "success": False}), 500