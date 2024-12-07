from flask import g, current_app, request, jsonify
# from app import auth
from app.models import Agent
from itsdangerous import (
    URLSafeTimedSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)
from app.schemas import AgentSchema, InsuranceCompanySchema, DistributorSchema
from app.models import Agent
from flask_jwt_extended import create_access_token, create_refresh_token


def sendOtp(email):
    
    user_info = Agent.query.filter_by(email=email).first()
    user_schema = AgentSchema()
    user_data = user_schema.dump(user_info)

    access_token = create_access_token({"email": email, "role": user_data.get('account_type')})
    refresh_token = create_refresh_token(email)
    return {"accessToken": access_token, "user": user_data, "refreshToken": refresh_token}

# 
# Register an Agent
# 
def registerUser(user, password):
    user.id = None

    # Encrypt password
    user.set_password(password)

    user.save()

    user_schema = AgentSchema()
    user_data = user_schema.dump(user)

    access_token, refresh_token = generate_auth_token(user_data)
    
    return {"accessToken": access_token, "user": user_data, "refreshToken": refresh_token}


# 
# Register a distributor
# 
def registerDistributor(distributor, password):
    distributor.id = None

    # Encrypt password
    distributor.set_password(password)

    distributor.save()

    distributor_schema = DistributorSchema()
    distributor_data = distributor_schema.dump(distributor)
    access_token, refresh_token = generate_auth_token(distributor_data)

    return {"accessToken": access_token, "user": distributor_data, "refreshToken": refresh_token}

# 
# Register an innsurance company
# 
def registerInsuranceCompany(insurance_company, password):
    insurance_company.id = None

    # Encrypt password
    insurance_company.set_password(password)

    insurance_company.save()

    insurance_schema = InsuranceCompanySchema()
    insurance_data = insurance_schema.dump(insurance_company)
    access_token, refresh_token = generate_auth_token(insurance_data)
    
    return {"accessToken": access_token, "user": insurance_data, "refreshToken": refresh_token}


# 
# Login agent
# 

def loginUser(user):
    
    user_email = user.get('email')
    user_info = Agent.query.filter_by(email=user_email).first()
    user_schema = AgentSchema()
    user_data = user_schema.dump(user_info)

    access_token, refresh_token = generate_auth_token(user_data)

    return {"accessToken": access_token, "user": user_data, "refreshToken": refresh_token}


#
# Generates a new authentication token.
#
def generate_auth_token(user_data, access_only=False):
    access_token = create_access_token({"email": user_data['email'], "role": user_data.get('account_type')})

    refresh_token = None

    if not access_only:
        refresh_token = create_refresh_token({"email": user_data['email'], "role": user_data.get('account_type')})

    return access_token, refresh_token


#
# Verify basic authentication.
#
# This function is called automatically by Flask to verify basic authentication. The credentials will either
# the user's actual credentials or a generated token.
#
# @auth.verify_password
def verify_password(username_or_token, password):
    current_app.logger.info(request)
    # first try to authenticate by token
    [user, message] = verify_auth_token(username_or_token)
    verified_by_token = True
    if not user:
        # try to authenticate with username/password
        user = Agent.query.filter_by(username=username_or_token).first()
        verified_by_token = False
        if not user or not user.verify_password(password):
            if(user):
                current_app.logger.error("message: \"login failed\", reason: \"incorrect password\", username: \"{}\", ip: \"{}\"".format(user.username, request.remote_addr))
                return False
            else:
                current_app.logger.error("message: \"login failed\", reason: \"incorrect username/{}\", ip: \"{}\"".format(message, request.remote_addr))
            return False
    g.user = user
    # If session times out, this prints the token
    if not verified_by_token:
        current_app.logger.info("message: \"login successful\", username: \"{}\", ip: \"{}\"".format(user.username, request.remote_addr))
    else:
        current_app.logger.info("message: \"logged in with token\", ip: \"{}\"".format(request.remote_addr))
    return True


#
# Verify authentication token.
#
# This function will verify that a generated token is valid.
#
def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        message = "expired token"
        return [None, message]  # valid token, but expired
    except BadSignature:
        message = "invalid token"
        return [None, message] # invalid token
    user = Agent.query.get(data['id'])
    return [user, ""]
