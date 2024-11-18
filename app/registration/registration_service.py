from app.schemas import UserSchema
from app.models import User
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

def registerUser(user, password):
    user.id = None

    # Encrypt password
    user.set_password(password)

    user.save()

    user_schema = UserSchema()
    user_data = user_schema.dump(user)
    return user_data

def loginUser(user):
    
    user_email = user.get('email')
    user_info = User.query.filter_by(email=user_email).first()
    user_schema = UserSchema()
    user_data = user_schema.dump(user_info)

    access_token = create_access_token({"email": user_email, "role": user_data.get('account_type')})
    refresh_token = create_refresh_token(user_email)
    return {"accessToken": access_token, "user": user_data, "refreshToken": refresh_token}

