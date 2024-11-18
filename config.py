import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    APPLICATION_ROOT = "/app"
