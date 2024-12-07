from app import db
from flask import abort
from app.models import Agent, Distributor, ApprovalRequest, Profile
from app.schemas import ProfileSchema, AgentSchema, DistributorSchema, SummaryDistributorSchema, RequestSchema, AgentRequestStatusEnum

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
def create_profile(user_details):

    profile = Profile(**user_details)

    profile.save()

    profile_schema = ProfileSchema()
    profile_data = profile_schema.dump(profile)

    print(profile_data)
    
    return profile_data

# Get profile
def get_profile(id):
    # Query the Profile model by the provided ID
    profile = Profile.get_user_by_id(id)
    
    if not profile:
        # If no profile found, raise a 404 error
        abort(404, description=f"Profile with ID {id} not found.")
    
    # Serialize the profile data using ProfileSchema
    profile_data = ProfileSchema().dump(profile)
    
    return profile_data


# 
#  Get Distributor by id
#   
def get_distributor(id):
    distributor = Distributor.query.filter_by(id=id).first()
    if not distributor:
        abort(404, description=f"Distributor not found.")
    
    return AgentSchema().dump(distributor)

# 
#  Get Distributor by email
#   
def get_distributor_by_email(distributor_email):
    # Retrieve distributor by email
    distributor_data = Distributor.get_user_by_email(distributor_email)
    
    if not distributor_data:
        abort(404, description="Distributor not found")

    return distributor_data

# 
#  Get Agent by id
#   
def get_agent(id):
    agent = Agent.get_user_by_id(id)
    if not agent:
        abort(404, description=f"Agent not found.")
    
    return AgentSchema().dump(agent)

# 
# check if agent is attached to a distributor already. Return error if linked else return agent instance
# 

def check_agent_distributor_status(agent_id):

    agent = Agent.get_user_by_id(agent_id)

    if not agent:
        abort(404, description=f"Agent not found.")

    if agent.distributor_id is not None:
        abort(409, description=f"Agent is not allowed to request approval from multiple Distributors.")

    return agent


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
#  Agent Request approval from distributor
#   

def request_approval(agent_id, distributor_id):

    # Get the agent's data from the database
    agent = get_agent(agent_id)
    
    distributor = get_distributor(distributor_id)

    agent = check_agent_distributor_status(agent_id)

    # Check if there's already a pending request
    existing_request = ApprovalRequest.get_pending_request(agent_id, distributor_id)

    if existing_request:
        abort(409, description=f"There is already a pending request for approval with this distributor.")
    
    # Create the new approval request
    approval_request = ApprovalRequest(agent_id=agent_id, distributor_id=distributor_id)
    approval_request.save()

    return  "Approval request sent successfully! Awaiting distributor's response."


# 
#  Retrieve all requests made to a distributor from agents
#   

def get_agent_requests(distributor_email, request_id=None):

    distributor_id = get_distributor_by_email(distributor_email).id

    if not request_id:

        all_requests = ApprovalRequest.query.filter_by(distributor_id=distributor_id)

        return RequestSchema().dump(all_requests, many=True)

    request = ApprovalRequest.query.filter_by(id=request_id, distributor_id=distributor_id).first()
    
    if not request:
        abort(403, description="No Data to Display")
    
    # Serialize the request data
    formatted_request = RequestSchema().dump(request)
        

    return formatted_request


def approve_and_add_agent(request_id, distributor_email, status):

    distributor_id = get_distributor_by_email(distributor_email).id

    approval_request = ApprovalRequest.get_request_by_id(request_id)

    agent = check_agent_distributor_status(approval_request.agent_id)

    approval_request.status = AgentRequestStatusEnum[status]

    approval_request.save()

    if status == 'ACCEPTED':

        agent.distributor_id = distributor_id
        agent.save()

    return  f"Agent request '{AgentRequestStatusEnum[status]}' successfully!"

    