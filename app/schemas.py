from app import ma
from flask import current_app
from app.models import Agent, Distributor, Purchase
from marshmallow import fields, validates, validates_schema, ValidationError
from werkzeug.security import check_password_hash
import re


#
# Response representation of a Agent
#
class AgentSchema(ma.SQLAlchemyAutoSchema):
    distributor = fields.Nested('DistributorSchema', only=['business_name', 'contact_email', 'phone_number'])
    class Meta:
        model = Agent
        exclude = [ 'kyc_document_url', 'password', 'updated', 'created']
        load_instance=True

#
# Response representation of a Distributor
#
class DistributorSchema(ma.SQLAlchemyAutoSchema):
    agents = fields.Nested('AgentSchema', many=True, exclude=['otp_verified', 'distributor'])

    class Meta:
        model = Distributor
        exclude = [ 'kyc_document_url', 'password', 'updated', 'created']
        load_instance=True

#
# Response representation of a Distributor
#
class SummaryDistributorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Distributor
        fields = ["id", "business_name", "contact_email", "phone_number"]


#
# Response representation of a Purchase
#
class PurchaseSchema(ma.SQLAlchemyAutoSchema):
    agent = fields.Nested(AgentSchema, only=['id', 'firstname', 'lastname'])
    
    class Meta:
        model = Purchase
        load_instance=True

#
# Validates user registration input.
#
class AgentOtpSchema(ma.SQLAlchemyAutoSchema):
    email = fields.String(required=True)

    
    @validates_schema
    def validate_registration(self, data, **kwargs):
        # Create error
        userinfo = data
        valerr = ValidationError({})
        foundError = False

        if "email" not in userinfo or userinfo["email"] == "":
            valerr.messages["email"] = "Email field is blank."
            foundError = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", userinfo["email"]):
            valerr.messages["email"] = "Invalid email address."
            foundError = True


        if foundError:
            raise valerr

#
# Validates user registration input.
#
class AgentRegistrationSchema(ma.SQLAlchemyAutoSchema):
    firstname = fields.String(required=True)
    lastname = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(require=True, load_only=True)

    class Meta:
        model = Agent
        load_instance = True

    
    @validates_schema
    def validate_registration(self, data, **kwargs):
        # Create error
        userinfo = data
        valerr = ValidationError({})
        foundError = False

        if "firstname" not in userinfo or userinfo["firstname"] == "":
            valerr.messages["firstname"] = "Firstname field is blank."
            foundError = True
        elif len(userinfo["firstname"]) < 3:
            valerr.messages["firstname"] = "Firstname is too short."
            foundError = True

        if "lastname" not in userinfo or userinfo["lastname"] == "":
            valerr.messages["lastname"] = "Lastname field is blank."
            foundError = True
        elif len(userinfo["lastname"]) < 3:
            valerr.messages["lastname"] = "Lastname is too short."
            foundError = True

        if "email" not in userinfo or userinfo["email"] == "":
            valerr.messages["email"] = "Email field is blank."
            foundError = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", userinfo["email"]):
            valerr.messages["email"] = "Invalid email address."
            foundError = True
        
        else:
            # Check if email already exists in the database
            existing_user = Agent.query.filter_by(email=userinfo["email"]).first()
            if existing_user:
                valerr.messages["email"] = "Email is already registered."
                foundError = True

        if "password" not in userinfo or userinfo["password"] == "":
            valerr.messages["password"] = "Password field is blank."
            foundError = True
        elif len(userinfo["password"]) < 8:
            valerr.messages["password"] = "Password is too short. Must be 8 or more characters"
            foundError = True
        elif not (re.match("\w*[A-Z]", userinfo["password"])
                and re.match("\w*[a-z]", userinfo["password"])
                and re.match("\w*[0-9]", userinfo["password"])):
            valerr.messages["password"] = "Password must include an uppercase character, lowercase character, and number."
            foundError = True
        elif "confirm_password" not in userinfo or userinfo["confirm_password"] == "":
            valerr.messages["confirm_password"] = "Please enter the password again."
            foundError = True
        elif userinfo["password"] != userinfo["confirm_password"]:
            valerr.messages["confirm_password"] = "Passwords must match."
            foundError = True

        if foundError:
            raise valerr

    def load(self, data, *args, **kwargs):
       
        data['is_active'] = False
        data['email'] = data['email'].lower()
        return super().load(data, *args, **kwargs)

#
# Validates user registration input.
#
class DistributorRegistrationSchema(ma.SQLAlchemyAutoSchema):
    business_name = fields.String(required=True)
    representative_name = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(require=True, load_only=True)

    class Meta:
        model = Distributor
        load_instance = True

    
    @validates_schema
    def validate_registration(self, data, **kwargs):
        # Create error
        userinfo = data
        valerr = ValidationError({})
        foundError = False

        if "business_name" not in userinfo or userinfo["business_name"] == "":
            valerr.messages["business_name"] = "Business_name field is blank."
            foundError = True

        elif len(userinfo["business_name"]) < 3:
            valerr.messages["business_name"] = "Business_name is too short."
            foundError = True

        else:
            # Check if email already exists in the database
            existing_dealer = Distributor.query.filter_by(business_name=userinfo["business_name"]).first()
            if existing_dealer:
                valerr.messages["email"] = "Business is already registered."
                foundError = True
                

        if "representative_name" not in userinfo or userinfo["representative_name"] == "":
            valerr.messages["representative_name"] = "Representative_name field is blank."
            foundError = True
        elif len(userinfo["representative_name"]) < 3:
            valerr.messages["representative_name"] = "Representative_name is too short."
            foundError = True
        
        else:
            # Check if email already exists in the database
            existing_dealer = Distributor.query.filter_by(representative_name=userinfo["representative_name"]).first()
            if existing_dealer:
                valerr.messages["email"] = "Representative is already registered."
                foundError = True

        if "email" not in userinfo or userinfo["email"] == "":
            valerr.messages["email"] = "Email field is blank."
            foundError = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", userinfo["email"]):
            valerr.messages["email"] = "Invalid email address."
            foundError = True
        
        else:
            # Check if email already exists in the database
            existing_dealer = Distributor.query.filter_by(email=userinfo["email"]).first()
            if existing_dealer:
                valerr.messages["email"] = "Email is already registered."
                foundError = True

        if "password" not in userinfo or userinfo["password"] == "":
            valerr.messages["password"] = "Password field is blank."
            foundError = True
        elif len(userinfo["password"]) < 8:
            valerr.messages["password"] = "Password is too short. Must be 8 or more characters"
            foundError = True
        elif not (re.match("\w*[A-Z]", userinfo["password"])
                and re.match("\w*[a-z]", userinfo["password"])
                and re.match("\w*[0-9]", userinfo["password"])):
            valerr.messages["password"] = "Password must include an uppercase character, lowercase character, and number."
            foundError = True
        elif "confirm_password" not in userinfo or userinfo["confirm_password"] == "":
            valerr.messages["confirm_password"] = "Please enter the password again."
            foundError = True
        elif userinfo["password"] != userinfo["confirm_password"]:
            valerr.messages["confirm_password"] = "Passwords must match."
            foundError = True

        if foundError:
            raise valerr

    def load(self, data, *args, **kwargs):

        data['is_active'] = False
        data['email'] = data['email'].lower()
        return super().load(data, *args, **kwargs)


#
# Validates user Login input.
#

class AgentLoginSchema(ma.SQLAlchemyAutoSchema):
    email = fields.String(required=True)
    password = fields.String(required=True)


    @validates_schema
    def validate_login(self, data, **kwargs):
        userinfo = data
        valerr = ValidationError({})
        foundError = False


        # Validate password field
        if "password" not in userinfo or userinfo["password"] == "":
            valerr.messages["password"] = "Password is required"
            foundError = True


        # Validate email field
        if "email" not in userinfo or userinfo["email"] == "":
            valerr.messages["email"] = "Email is required"
            foundError = True
        else:
            # Check if email exists in the database
            existing_user = Agent.query.filter_by(email=userinfo["email"]).first()
            if not existing_user:
                valerr.messages["email"] = "Invalid email or password"
                foundError = True
            else:
                # Email exists, now check the password
                if not check_password_hash(existing_user.password, userinfo["password"]):
                    valerr.messages["password"] = "Invalid email or password"
                    foundError = True

        if foundError:
            raise valerr

#
# Validates new purchase order.
#
class PurchaseRegistrationSchema(ma.SQLAlchemyAutoSchema):
    firstname = fields.String(required=True)
    lastname = fields.String(required=True)
    email = fields.String(required=True)
    product_category = fields.String(required=True)
    product = fields.String(required=True)
    phone_number = fields.String(required=True)
    agent_id = fields.String()

    class Meta:
        model = Purchase
        load_instance = True

    
    @validates_schema
    def validate_purchase(self, data, **kwargs):
        # Create error
        userinfo = data
        valerr = ValidationError({})
        foundError = False

        if "firstname" not in userinfo or userinfo["firstname"] == "":
            valerr.messages["firstname"] = "Firstname field is blank."
            foundError = True
        elif len(userinfo["firstname"]) < 3:
            valerr.messages["firstname"] = "Firstname is too short."
            foundError = True

        if "lastname" not in userinfo or userinfo["lastname"] == "":
            valerr.messages["lastname"] = "Lastname field is blank."
            foundError = True
        elif len(userinfo["lastname"]) < 3:
            valerr.messages["lastname"] = "Lastname is too short."
            foundError = True

        if "email" not in userinfo or userinfo["email"] == "":
            valerr.messages["email"] = "Email field is blank."
            foundError = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", userinfo["email"]):
            valerr.messages["email"] = "Invalid email address."
            foundError = True
        

        if "product_category" not in userinfo or userinfo["product_category"] == "":
            valerr.messages["product_category"] = "Product_category field is blank."
            foundError = True

        if "product" not in userinfo or userinfo["product"] == "":
            valerr.messages["product"] = "Product field is blank."
            foundError = True

        if "phone_number" not in userinfo or userinfo["phone_number"] == "":
            valerr.messages["phone_number"] = "Phone Number field is blank."
            foundError = True
       

        if foundError:
            raise valerr

    # def load(self, data, *args, **kwargs):
    #     """
    #     Override the load method to ensure 'type' gets assigned even if it's not provided
    #     """
    #     if not isinstance(data.get("type"), str):
    #         data['account_type'] = 'dealer'
    #     data['is_active'] = False
    #     data['email'] = data['email'].lower()
    #     return super().load(data, *args, **kwargs)