from app import ma
from flask import current_app
from app.models import Profile, Agent, Distributor, Purchase, ApprovalRequest, InsuranceCompany
from marshmallow import fields, validates_schema, ValidationError, EXCLUDE, post_load
from werkzeug.security import check_password_hash
import re
from enum import Enum


# Define the Enum for valid status values
class AgentRequestStatusEnum(Enum):
    PENDING = "pending"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


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


class InsuranceCompanySchema(ma.SQLAlchemyAutoSchema):
    # Include fields from related models (for example, distributor)
    distributor = fields.Nested('DistributorSchema', only=['business_name', 'contact_email', 'phone_number'])
    
    # Meta class to specify model and exclude some fields from serialization
    class Meta:
        model = InsuranceCompany
        exclude = ['kyc_document_url', 'password', 'updated', 'created']
        load_instance = True

    @post_load
    def process_data(self, data, **kwargs):
        # This method allows us to modify or clean the data after it's been loaded
        if 'email' in data:
            data['email'] = data['email'].lower()  # Standardize email to lowercase
        return data
    

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
# Response representation of a Approval Requests
#
class RequestSchema(ma.SQLAlchemyAutoSchema):
    agent = fields.Nested('AgentSchema', exclude=['otp_verified', 'distributor'])

    class Meta:
        model = ApprovalRequest
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


# Agent request status validation schema
class AgentRequestStatusSchema(ma.SQLAlchemyAutoSchema):
    status = fields.String(required=True)

    @validates_schema
    def validate_input(self, user_input, **kwargs):
        # Create error instance
        valerr = ValidationError({})
        foundError = False

        # Validate the 'status' field
        status = user_input.get("status")

        if not status or status == "":
            valerr.messages["status"] = "Status is required!"
            foundError = True
        elif status not in AgentRequestStatusEnum.__members__:
            valerr.messages["status"] = f"Invalid status"
            foundError = True

        # If errors found, raise the ValidationError with collected messages
        if foundError:
            raise valerr


#
# Schema for all profile.
#
class ProfileSchema(ma.SQLAlchemyAutoSchema):


    class Meta:
        model = Profile
        load_instance = False
        partial = True
        unknown = EXCLUDE

    def __init__(self, *args, **kwargs):
        # Pop the 'exclude_fields' argument if provided
        exclude_fields = kwargs.pop('exclude_fields', [])

        # Call the parent constructor to initialize the schema
        super().__init__(*args, **kwargs)

        # Remove excluded fields from the schema's fields
        for field in exclude_fields:
            if field in self.fields:
                del self.fields[field]

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
# Validates user registration input for Insurance Company
#
class InsuranceCompanyRegistrationSchema(ma.SQLAlchemyAutoSchema):
    company_name = fields.String(required=True)
    contact_email = fields.String(required=True)
    contact_phone = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(required=True, load_only=True)

    class Meta:
        model = InsuranceCompany  # Assuming you have an InsuranceCompany model
        load_instance = True

    @validates_schema
    def validate_registration(self, data, **kwargs):
        # Create error
        userinfo = data
        valerr = ValidationError({})
        foundError = False

        # Validate company_name
        if "company_name" not in userinfo or userinfo["company_name"] == "":
            valerr.messages["company_name"] = "Company_name field is blank."
            foundError = True
        elif len(userinfo["company_name"]) < 3:
            valerr.messages["company_name"] = "Company_name is too short."
            foundError = True
        else:
            # Check if company_name already exists in the database
            existing_company = InsuranceCompany.query.filter_by(company_name=userinfo["company_name"]).first()
            if existing_company:
                valerr.messages["company_name"] = "Company name is already registered."
                foundError = True

        # Validate contact_email
        if "contact_email" not in userinfo or userinfo["contact_email"] == "":
            valerr.messages["contact_email"] = "Contact_email field is blank."
            foundError = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", userinfo["contact_email"]):
            valerr.messages["contact_email"] = "Invalid email address."
            foundError = True
        else:
            # Check if contact_email already exists in the database
            existing_company = InsuranceCompany.query.filter_by(contact_email=userinfo["contact_email"]).first()
            if existing_company:
                valerr.messages["contact_email"] = "Contact email is already registered."
                foundError = True

        # Validate email
        if "email" not in userinfo or userinfo["email"] == "":
            valerr.messages["email"] = "Email field is blank."
            foundError = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", userinfo["email"]):
            valerr.messages["email"] = "Invalid email address."
            foundError = True
        else:
            # Check if email already exists in the database
            existing_company = InsuranceCompany.query.filter_by(email=userinfo["email"]).first()
            if existing_company:
                valerr.messages["email"] = "Email is already registered."
                foundError = True

        # Validate contact_phone
        if "contact_phone" not in userinfo or userinfo["contact_phone"] == "":
            valerr.messages["contact_phone"] = "Contact_phone field is blank."
            foundError = True
        elif len(userinfo["contact_phone"]) < 10:
            valerr.messages["contact_phone"] = "Contact_phone number is too short."
            foundError = True

        # Validate password
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
        data['is_active'] = False  # Default value for the new insurance company
        data['email'] = data['email'].lower()  # Store email in lowercase
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