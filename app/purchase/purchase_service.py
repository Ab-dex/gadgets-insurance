from app.schemas import PurchaseSchema, AgentSchema
from flask import jsonify, abort
from app.models import Purchase, Agent
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from marshmallow.exceptions import ValidationError
from app.schemas import PurchaseRegistrationSchema


def getAllPurchases():
    try:
        purchases = Purchase.query.options(joinedload(Purchase.agent)).all()

        products_schema = PurchaseSchema(many=True)
        products = products_schema.dump(purchases)

        return products
    
    except SQLAlchemyError as e:
        
        return jsonify({"error": "An error occurred while fetching purchases"}), 500
    
    except Exception as e:
       
        return jsonify({"error": "An unexpected error occurred"}), 500

def get_purchase_by_id(purchase_id):
    try:

        
        # Query the Purchase model for the purchase with the given ID
        purchase = Purchase.query.get(purchase_id)
        
        # If no purchase is found, return a 404 error
        if not purchase:
            abort(404, description=f"Purchase not found.")
        
        # Serialize the purchase data using PurchaseSchema
        purchase_schema = PurchaseSchema()
        purchase_data = purchase_schema.dump(purchase)

        # Return the serialized purchase data as JSON
        return purchase_data

    except ValidationError as ve:
        abort(400, description= str(e))

    except SQLAlchemyError as e:
        # Handle any SQLAlchemy errors (e.g., database connection issues)
        abort(500, description= str(e))


def registerNewPurchase(data):
    try:

        new_buyer = PurchaseRegistrationSchema().load(data)
        
        new_buyer.save()
        
        products_schema = PurchaseSchema()
        product = products_schema.dump(data)
        
        return product
    
    except ValidationError as ve:
       
        print(f"Validation error occurred: {str(ve)}")
        return jsonify({"error": "Validation failed", "message": str(ve)}), 400
    
    except SQLAlchemyError as e:
        
        print(f"Database error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while registering the purchase"}), 500
    
    except Exception as e:
       
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500



def get_agent_id_from_user(email):
    try:
        user_info = Agent.get_user_by_email(email)
        
        if not user_info:
            raise ValueError(f"Agent with email {email} does not exist.")

        user_schema = AgentSchema()
        user_data = user_schema.dump(user_info)
        
        return user_data['id']
    
    except ValueError as e:
        print(str(e))
        return None
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None