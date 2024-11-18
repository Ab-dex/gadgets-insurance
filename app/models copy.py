from sqlalchemy.orm import relationship

from app import db

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils import Timestamp
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import ActivityPlugin;
import sqlalchemy as sa
from uuid import uuid4

import enum

# Setup Activity Plugin
activity_plugin = ActivityPlugin()
make_versioned(plugins=[activity_plugin])


#
# Enum: User Type
#
class UserType(enum.Enum):
    admin = "admin"
    inssurance = "insurance"
    dealer = "dealer"
    user = "user"


#
# Model: Base
#
class BaseModel(db.Model, Timestamp):
    __abstract__ = True


#
# Model: User
#

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True, default=str(uuid4()))
    username = db.Column(db.String(64))
    email = db.Column(db.String(120))
    password = db.Column(db.String(128))
    # phone_number = db.Column(db.String(15))
    # otp = db.Column(db.String(6), nullable=True)
    # otp_verified = db.Column(db.Boolean, default=False)
    # kyc_status = db.Column(db.String(20), default="pending")
    # kyc_document_url = db.Column(db.String(255))
    # dealer_id = db.Column(db.String(36), db.ForeignKey('dealers.id'), nullable=True)
    # issuer_id = db.Column(db.String(36), db.ForeignKey('issuers.id'), nullable=True)
    # is_active = db.Column(db.Boolean(), default=False)
    # account_type = db.Column(db.String(16))

    # dealer = db.relationship('Dealer', backref='dealer_users')
    # issuer = db.relationship('Issuer', backref='user_issuers')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    # def __repr__(self):
    #     return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    # def verify_password(self, password):
    #     return check_password_hash(self.password, password)

    # def is_admin(self):
    #     return self.account_type == UserType.admin.value

    # @classmethod
    # def get_user_by_id(cls, id):
    #     return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


#
# Model: Dealer
#
class Dealer(BaseModel):
    __tablename__ = 'dealers'
    
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    business_name = db.Column(db.String(120), nullable=False)
    representative_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    kyb_status = db.Column(db.String(20), default="pending")
    kyc_status = db.Column(db.String(20), default="pending")
    business_document_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean(), default=False)
    account_type = db.Column(db.String(16))

    # users = db.relationship("User", backref="dealer_users", lazy=True)

    def __repr__(self):
        return f"<Dealer {self.business_name}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.account_type == UserType.admin.value

    @classmethod
    def get_dealer_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


#
# Model: Issuer
#
class Issuer(BaseModel):
    __tablename__ = 'issuers'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    company_name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    contact_email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean(), default=False)
    registration_status = db.Column(db.String(20), default="pending")
    kyb_status = db.Column(db.String(20), default="pending")
    kyb_document_url = db.Column(db.String(255))
    account_type = db.Column(db.String(16))

    ratings = db.relationship("Rating", backref="issuer", lazy=True)
    # users = db.relationship("User", backref="user_issuers", lazy=True)

    def __repr__(self):
        return '<Issuer {}>'.format(self.company_name)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.account_type == UserType.admin.value

    @classmethod
    def get_company_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


#
# Model: Rating value
#
class RatingValue(BaseModel):
    __tablename__ = 'rating_value'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False, unique=True)
    
    def __repr__(self):
        return f"<RatingValue {self.value}>"
    
    @staticmethod
    def create_default_ratings():
        # Add predefined ratings from 1 to 5
        for i in range(1, 6):
            db.session.add(RatingValue(value=i))
        db.session.commit()


#
# Model: Rating
#
class Rating(BaseModel):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(256), nullable=False)
    # user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    issuer_id = db.Column(db.String(36), db.ForeignKey('issuers.id'), nullable=False)

    def __repr__(self):
        return '<Rating {}>'.format(self.value)


sa.orm.configure_mappers()
Activity = activity_plugin.activity_cls