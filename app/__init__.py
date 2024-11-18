from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource
from config import Config
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from flask.logging import default_handler
import app.filters as filters_util
import logging
from app.models import Distributor, Agent
from app.extensions import db, jwt
from .services.cloudinary_service import CloudinaryService


migrate = Migrate()
auth = HTTPBasicAuth()
ma = Marshmallow()

filters = filters_util


def create_app(config_class=Config):
    application = Flask(__name__)
    Api(application)
    application.config.from_object(config_class)

    db.init_app(application)
    ma.init_app(application)
    jwt.init_app(application)
    migrate.init_app(application, db)

    # Initialize the CloudinaryService
    cloudinary_service = CloudinaryService()

    # pass the service instance where needed
    application.cloudinary_service = cloudinary_service

    # from app.error import bp as error_bp
    # application.register_blueprint(error_bp)

    from app.authentication import bp as authentication_bp
    application.register_blueprint(authentication_bp, url_prefix="/api")

    # from app.registration import bp as registration_bp
    # application.register_blueprint(registration_bp, url_prefix="/api")

    from app.user import bp as user_bp
    application.register_blueprint(user_bp, url_prefix="/api")

    from app.purchase import bp as purchase_bp
    application.register_blueprint(purchase_bp, url_prefix="/api")

    from app.middlewares import errors_bp
    application.register_blueprint(errors_bp)

    # class AgentSchema(ma.SQLAlchemyAutoSchema):
    #     class Meta:
    #         model = Agent
    #         load_instance = True

    # #jwt user loader
    # @jwt.user_lookup_loader
    # def user_lookup_callback(_jwt_headers, jwt_data):

    #     identity = jwt_data['sub']
    #     if identity['role'] is None:
    #         identity_instance = Agent.query.filter_by(email = identity['email']).one_or_none()
    #         details = AgentSchema().dump(identity_instance)
    #         return details
    #     return Distributor.query.filter_by(email = identity['email']).one_or_none()

    CORS(application, resources={r"/*": {"origins": "*"}})

    application.logger.setLevel('INFO') # Configurable log level

    # Remove default logger
    application.logger.removeHandler(default_handler)

    # Doing this duplicates the log stream, but allows for custom logs
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter("level \"%(levelname)s\", %(message)s"))
    application.logger.addHandler(lh)

    return application


from app import models, schemas
