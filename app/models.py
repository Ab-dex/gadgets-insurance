from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils import Timestamp
from uuid import uuid4
from sqlalchemy import String, ARRAY
from datetime import datetime
#
# Model: Base
#
class BaseModel(db.Model, Timestamp):
    __abstract__ = True

class UserTypes(db.Enum):
    AGENT = 'agent'
    ADMIN = 'admin'
    DISTRIBUTOR = 'distributor'

#
# Model: Agent
#

class Agent(BaseModel):
    __tablename__ = 'agent'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    lastname = db.Column(db.String(64), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120),  unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(15))
    otp_verified = db.Column(db.Boolean(), default=False)
    kyc_status = db.Column(db.String(20), default="pending")
    kyc_document_url = db.Column(db.String(255))
    is_approved = db.Column(db.Boolean(), default=False)
    is_active = db.Column(db.Boolean(), default=False)
    account_type  = db.Column(db.Integer, default=1)

    distributor_id = db.Column(db.String(36), db.ForeignKey('distributor.id'))
    profile_id = db.Column(db.String(36), db.ForeignKey('profile.id'))

    def __repr__(self):
        return '<Agent {}>'.format(self.firstname)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


#
# Model: Dealer
#
class Distributor(BaseModel):
    __tablename__ = 'distributor'
    
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    business_name = db.Column(db.String(120), unique=True, nullable=False)
    representative_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    contact_email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    otp_verified = db.Column(db.Boolean(), default=False)
    email_verified = db.Column(db.Boolean(), default=False)
    phone_verified = db.Column(db.Boolean(), default=False)
    kyb_status = db.Column(db.String(20), default="pending")
    kyc_status = db.Column(db.String(20), default="pending")
    kyc_document_url = db.Column(db.String(255))
    business_document_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean(), default=False)
    account_type  = db.Column(db.Integer, default=2)

    profile_id = db.Column(db.String(36), db.ForeignKey('profile.id'))

    agents = db.relationship('Agent', backref='distributor', lazy=True)
    # purchases = db.relationship('Purchase', backref='distributor', lazy=True)


    def __repr__(self):
        return f"<Distributor {self.business_name}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


#
# Model: Purchases
#

class Purchase(BaseModel):
    __tablename__ = 'purchase'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    lastname = db.Column(db.String(64), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    product_category = db.Column(db.String(120), nullable=False)
    product = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    receipt_image = db.Column(db.String(255), nullable=True)
    product_image = db.Column(db.String(255), nullable=True)
    purchase_status = db.Column(db.String(20), default='pending')
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_secret = db.Column(db.String(20), unique=True, nullable=False)


    agent_id = db.Column(db.String(36), db.ForeignKey('agent.id'), nullable=False)
    distributor_id = db.Column(db.String(36), db.ForeignKey('distributor.id'), nullable=True)

    agent = db.relationship('Agent', backref='purchases', lazy=True)
    # distributor = db.relationship('Distributor', backref='purchases')

    # insurance_company_id = Column(Integer, ForeignKey('insurance_companies.id'))
    # insurance_company = relationship('InsuranceCompany', backref='purchases')

    def __repr__(self):
        return '<Purchase {}>'.format(self.product)

    @classmethod
    def get_purchase_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# 
# Profile model
# 
class Profile(BaseModel):
    __tablename__ = 'profile'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    lastname = db.Column(db.String(64), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120),  unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    account_type  = db.Column(db.Integer, default=1)
    profile_image = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    country = db.Column(db.String(120), nullable=True)

    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()




class ApprovalRequest(BaseModel):
    __tablename__ = 'approval_request'
    
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    agent_id = db.Column(db.String(36), db.ForeignKey('agent.id'), nullable=False)
    distributor_id = db.Column(db.String(36), db.ForeignKey('distributor.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='request_status'), default='pending')
    
    # Relationships
    agent = db.relationship('Agent', backref='approval_requests', lazy=True)
    distributor = db.relationship('Distributor', backref='approval_requests', lazy=True)

    def __repr__(self):
        return f"<ApprovalRequest agent_id={self.agent_id}, distributor_id={self.distributor_id}, status={self.status}>"

    @classmethod
    def get_request_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_pending_request(cls, agent_id, distributor_id):
        return cls.query.filter_by(agent_id=agent_id, distributor_id=distributor_id, status='pending').first()


class InsuranceCompany(BaseModel):
    __tablename__ = 'insurance_company'

    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    company_name = db.Column(db.String(128), nullable=False)
    contact_email = db.Column(db.String(128), nullable=False)
    contact_phone = db.Column(db.String(64), nullable=False)
    kyb_status = db.Column(db.String(20), default="pending")
    is_verified = db.Column(db.Boolean(), default=False)
    account_type  = db.Column(db.Integer, default=3)
    otp_verified = db.Column(db.Boolean(), default=False)
    email_verified = db.Column(db.Boolean(), default=False)
    phone_verified = db.Column(db.Boolean(), default=False)
    kyc_status = db.Column(db.String(20), default="pending")
    kyc_document_url = db.Column(db.String(255))
    business_document_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean(), default=False)

    # policies = relationship('Policy', backref='insurance_company', lazy=True)

    def __repr__(self):
        return f"<InsuranceCompany(id={self.id}, name={self.company_name})>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Policy(db.Model):  # Updated for linkage
    id = db.Column(db.String(36), primary_key=True)
    agent_id = db.Column(db.String(36), db.ForeignKey('agent.id'), nullable=False)
    purchase_id = db.Column(db.String(36), db.ForeignKey('purchase.id'), nullable=False)
    insurance_company_id = db.Column(db.String(36), db.ForeignKey('insurance_company.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)