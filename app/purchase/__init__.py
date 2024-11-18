from flask import Blueprint

bp = Blueprint('purchase', __name__)

from app.purchase import purchase_routes
