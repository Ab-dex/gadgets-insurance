#
# Blueprint: User
#
# >> Make sure to import bp as the correct blueprint <<
#
from app.user import bp

from flask import jsonify, abort, request, g, current_app, abort
from marshmallow import ValidationError
from app import filters, db
from app.models import Agent, Distributor
from app.schemas import AgentSchema, AgentRequestStatusSchema
from app.user import user_service
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from app.authentication.decorators import is_admin
#
# Get all agents
#
@bp.route('/agents')
# @jwt_required()
def get_agents():
    agents = Agent.query.all()
    return AgentSchema().jsonify(agents, many=True)


#
# Get agent by username
#
@bp.get('/agents/<string:id>')
def get_agent_by_id(id):
    agent = user_service.get_agent(id)

    return jsonify({"data": agent, "success": True, "message": "Agent Retrieved Successfully!"}), 200

#
# Get agent by username
#
@bp.get('/profile/<string:id>')
@jwt_required()
def get_profile_by_id(id):
    agent = user_service.get_profile(id)

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


#
# Agent requests approval from distributor
#

@bp.post('/agents/request-approval')
@bp.post('/agents/request-approval/<string:agent_id>')
@jwt_required()
def request_approval(agent_id = None):

    current_user = get_jwt_identity()

    agent_email = current_user['email']

    if current_user['role'] != 'admin' and agent_id:
        abort(403, description="Forbidden request")

    if current_user['role'] != 'agent' or agent_email == None:
        abort(401, description="Unauthorized request")

    distributor_id = request.json.get('distributor_id')
    
    message = user_service.request_approval(agent_id, distributor_id)

    return jsonify({
        "data": {"agent_id": agent_id, "distributor_id": distributor_id},
        "success": True,
        "message": message
    }), 200


#
# Get all available distributor summary
#

@bp.get('/distributors')
@is_admin()
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
@jwt_required()
def get_distributor_by_id(id):
    try:
        data = user_service.get_distributor(id)

        return jsonify({"data": data, "success": True, "message": "Distributor Retrieved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400


#
# Distributor gets pending agent approval
#
@bp.get('/distributors/agent-requests')
@bp.get('/distributors/agent-requests/<string:request_id>')
@jwt_required()
def get_agent_requests(request_id=None):

    current_user = get_jwt_identity()

    distributor_email = current_user['email']

    data = None

    if request_id:
        # If request_id is provided, fetch the specific request
        data = user_service.get_agent_requests(distributor_email, request_id)
    
    else:
        data = user_service.get_agent_requests(distributor_email)

    return jsonify({ "success": True, "message": "Data retrieved Successfully", "data": data}), 200


#
# Update specific agent request
#
@bp.put('/distributors/agent-requests/<string:request_id>')
@jwt_required()
def update_agent_request(request_id):

    try:

        input_data = request.get_json()

        # Verify Email
        validated_data = AgentRequestStatusSchema().load(input_data)

        current_user = get_jwt_identity()

        distributor_email = current_user['email']

        data = user_service.approve_and_add_agent(request_id, distributor_email, validated_data['status'])
        
        return jsonify({ "success": True, "message": "Agent Approved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        abort(400, description=err.messages)

    except BadRequest as e:
        abort(400, description="Body cannot be empty!!")
        


#
# Get all Distributors data
#
@bp.get('/admin/distributors')
# @filters.is_admin
@jwt_required()
def get_distributors():
    try:
        
        data = user_service.get_all_distributors()

        return jsonify({"data": data, "success": True, "message": "Distributors Retrieved Successfully!"}), 200

    except ValidationError as err:
        current_app.logger.info(err.messages)
        return jsonify({"errors": err.messages, "success": False}), 400