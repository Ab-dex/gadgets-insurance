#
# Blueprint: User
#
# >> Make sure to import bp as the correct blueprint <<
#
from app.user import bp

from flask import jsonify, abort, request, g, current_app
from marshmallow import ValidationError
from app import filters, db
from app.models import Agent, Distributor
from app.schemas import AgentSchema
from app.user import user_service
from flask_jwt_extended import jwt_required

#
# Get all agents
#
@bp.route('/agents')
# @filters.is_admin
# @jwt_required()
def get_agents():
    agents = Agent.query.all()
    return AgentSchema().jsonify(agents, many=True)


#
# Get agent by username
#
@bp.route('/agents/<string:id>')
def get_agent_by_id(id):
    agent = user_service.get_agent(id)

    return jsonify({"data": agent, "success": True, "message": "Agent Retrieved Successfully!"}), 200


#
# Remove agent by id
#
@bp.route('/agents/<string:id>', methods=['DELETE'])
def remove_agent(id):
    if g.user.id != id and not g.user.is_admin():
        abort(401)

    user_service.delete_by_username(id)
    return '', 200

@bp.post('/agents/<string:agent_id>/request-approval')
# @jwt_required()
def request_approval(agent_id):

    # current_user = get_jwt_identity()
    

    # if current_user['role'] != 'agent' or current_user['id'] != agent_id:
    #     return jsonify({"errors": "Unauthorized", "success": False}), 403

    distributor_id = request.json.get('distributor_id')

    # if current_user['id'] != agent_id:
    #     return jsonify({"errors": "Unauthorized", "success": False}), 403
    
    message = user_service.request_approval(agent_id, distributor_id)

    return jsonify({
        "data": {"agent_id": agent_id, "distributor_id": distributor_id},
        "success": True,
        "message": message
    }), 200




#
# Get all Distributors data
#
@bp.route('/admin/distributors')
# @filters.is_admin
@jwt_required()
def get_distributors():
    try:
        
        data = user_service.get_all_distributors()

        return jsonify({"data": data, "success": True, "message": "Distributors Retrieved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400

#
# Get all available distributor summary
#

@bp.route('/distributors')

def get_distributors_summery():
    try:
        
        data = user_service.get_all_distributors_summary()

        return jsonify({"data": data, "success": True, "message": "Distributors Retrieved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400
    

#
# Get one distributor
#
@bp.get('/distributors/<string:id>')
# @filters.is_admin
@jwt_required()
def get_user_by_id(id):
    try:
        data = user_service.get_distributor(id)

        return jsonify({"data": data, "success": True, "message": "Distributor Retrieved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400

#
# Distributor approve agent
#
@bp.put('/distributors/<string:id>/approve-agent')
# @filters.is_admin
@jwt_required()
def add_agent_to_distributor(id):
    try:
        body_data = request.get_json()
        agent_id = body_data['agent_id']
        if not agent_id:
            return jsonify({"errors": "Agent ID is required", "success": False}), 400
        data = user_service.approve_and_add_agent(id, agent_id)

        return jsonify({ "success": True, "message": "Agent Approved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400
