from app import db
from flask import current_app, abort
from app.models import Agent, Distributor, ApprovalRequest
from app.schemas import AgentSchema, DistributorSchema, SummaryDistributorSchema

#
# Get user by username
#
def get_by_username(username):
    return Agent.query.filter_by(username=username).first()


#
# Save a user
#
def save(user):
    db.session.add(user)
    db.session.commit()
    return user


#
# Delete a user by username
#
def delete_by_username(username):
    user = get_by_username(username)
    db.session.delete(user)
    db.session.commit()
    return True

# 
#  Get Distributor by id
#   
def get_distributor(id):
    distributor = Distributor.query.filter_by(id=id).first()
    if not distributor:
        abort(404, description=f"Distributor not found.")
    
    return AgentSchema().dump(distributor)

# 
#  Get Agent by id
#   
def get_agent(id):
    agent = Agent.get_user_by_id(id)
    if not agent:
        abort(404, description=f"Agent not found.")
    
    return AgentSchema().dump(agent)

# 
#  Get all Distributors
#   
def get_all_distributors():

    distributors = Distributor.query.all()

    distributor_data = DistributorSchema().dump(distributors, many=True)
    return distributor_data

# 
#  Get all Distributors
#   
def get_all_distributors_summary():

    distributors = Distributor.query.all()

    distributor_data = SummaryDistributorSchema().dump(distributors, many=True)
    return distributor_data


# 
#  Agent Request approval from distributo
#   

def request_approval(agent_id, distributor_id):

    # Get the agent's data from the database
    agent = get_agent(agent_id)
    
    # Get the distributor ID from the request data (assumed to be passed in the request body)
    
    distributor = get_distributor(distributor_id)
    
    if not distributor:
        return jsonify({"errors": "Distributor not found", "success": False}), 404

    # Check if there's already a pending request
    existing_request = ApprovalRequest.get_pending_request(agent_id, distributor_id)
    if existing_request:
        return jsonify({
            "errors": "There is already a pending request for approval with this distributor.",
            "success": False
        }), 409  # Conflict
    
    # Create the new approval request
    approval_request = ApprovalRequest(agent_id=agent_id, distributor_id=distributor_id)
    approval_request.save()

    return  "Approval request sent successfully! Awaiting distributor's response."


# 
#  Distributor Approve an agent by  usingg their id
#   

def approve_and_add_agent(distributor_id, agent_id):

    distributor = get_distributor(distributor_id)

    agent = Agent.get_user_by_id(agent_id)

    if agent.distributor_id is not None:
        abort(409, description=f"Not allowed to request approval from multiple Distributors. Please resign yourself from current distributor first")

    agent.distributor_id = distributor_id

    agent.save()

    return  ''

    