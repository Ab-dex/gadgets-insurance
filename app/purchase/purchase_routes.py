from app.purchase import bp

from flask import request, url_for, current_app, jsonify, abort
from marshmallow import ValidationError
from app.schemas import PurchaseSchema
from sqlalchemy.exc import SQLAlchemyError
from app.purchase import purchase_service
from flask_jwt_extended import jwt_required, get_jwt_identity


#
# Register a new buyer
#
@bp.post('/purchase')
# @jwt_required()
def register_buyer():
    user_identity = get_jwt_identity()

    agent_id = purchase_service.get_agent_id_from_user(user_identity['email'])

    try:
        user_info = request.get_json()
        user_info['agent_id'] = agent_id
        user_info['purchase_secret'] = "A1B3"
        
        
        response = purchase_service.registerNewPurchase(user_info)

        return jsonify({ "success": True, "message": "Working", 'data': response})

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400
    

#
# Get all purchases
#
@bp.get('/purchase')
def get_purchases():
    response = purchase_service.getAllPurchases()

    return jsonify({ "success": True, "message": "All Sales Retrieved Successfully", "data": response})

#
# Get all purchases
#
@bp.get('/purchase/<purchase_id>')
def purchase_detail(purchase_id):

    # upload_result = current_app.cloudinary_service.upload_image("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg", "shoes")

    # print("uploading")

    # print(upload_result)
    response = purchase_service.get_purchase_by_id(purchase_id)

    return jsonify({ "success": True, "message": "Sale Retrieved Successfully", "data": response})