from app.purchase import bp

from flask import request, current_app, jsonify
from marshmallow import ValidationError
from app.purchase import purchase_service
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.random_secret import generate_secret


#
# Register a new buyer
#
@bp.post('/purchase')
# @jwt_required()
def register_buyer():
    user_identity = get_jwt_identity()

    agent_id = purchase_service.get_agent_id_from_user(user_identity['email'])

    try:
        purchase_info = request.get_json()
        purchase_info['agent_id'] = agent_id
        purchase_info['purchase_secret'] = generate_secret(8)
        
        
        response = purchase_service.registerNewPurchase(purchase_info)

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