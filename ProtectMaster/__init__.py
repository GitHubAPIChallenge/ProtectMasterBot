import logging
import os
import json
import pprint
import requests 
import azure.functions as func
from jsonschema import validate, ValidationError
from lib import github_client
from lib import github_token_client
from lib import cosmosdb_client

# ---------------------------------------------------------
# 
#  This is a main function for master branch protection process
# 
# ---------------------------------------------------------

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('ProtectMasterBot caught GitHub repository event.')

    # Get and set params from the request
    try: 
        request_body = json.loads(req.get_body())
        gh_event = request_body['action']
        gh_org = request_body['organization']['login']
        gh_repo = request_body['repository']['name']
        gh_default_branch = request_body['repository']['default_branch']
    except (KeyError, ValueError):  
        logging.error('Json payload was not valid')
        return func.HttpResponse("Error! Json payload was not valid.", status_code=500)

    # Get and set params from environment variables
    try: 
        connection_string = os.environ['cosmosdb_connection_string']
        app_id = os.environ["gh_app_id"]
        app_pem = os.environ["gh_app_pem"]
    except (KeyError, ValueError):
        logging.error('Could not read environment variables')
        return func.HttpResponse("Error! Please set environment variables", status_code=500)


    # Get org data from CosmosDB
    try:
        cc = cosmosdb_client.CosmosDBClient(connection_string, "apichallenge", "usersettings")
        org_data = cc.get(gh_org)
    except: 
        return func.HttpResponse("Error! Could not aquire the result from the db. Please reinstall GitHub Apps.", status_code=500)

    # Get org information from query result
    try: 
        installation_id = org_data["installation_id"]
        protection_json = org_data["protection_json"]
        mention = org_data["mention"]
    except KeyError:
        logging.error('Error! lack of some data')
        return func.HttpResponse("Error! Data stored in database is not well formatted.", status_code=500)

    # Make GitHub Apps issue a valid access token 
    gh_token_client = github_token_client.GitHubTokenClient(app_id, app_pem, installation_id)
    access_token = gh_token_client.get_token()

    # Open protection rules json parameters
    with open("config/protection_rules.json") as rule_file:
        branch_protection_default_rules = json.load(rule_file)

    # Read and check user rules
    rules = branch_protection_default_rules
    if protection_json != "":
        rules = json.loads(protection_json)

    if gh_event == 'created':
        gh_client = github_client.GitHubClient(access_token, gh_org, gh_repo, gh_default_branch)

        # Create README.md
        r = gh_client.create_readme()
        logging.info(f'README.md creation done with {r.status_code} code')

        # Protect Repository with protection rules
        r = gh_client.protect_repository(rules)
        logging.info(f'Branch Protection done with {r.status_code} code')

        if r.status_code == 200:
            # Create an Issue
            r = gh_client.create_issue(mention, rules)
            logging.info(f'Issue Creation done with {r.status_code} code')
            return func.HttpResponse(f"Successfully protected the branch!", status_code=200)
        else:
            # Create an Issue
            r = gh_client.create_issue(mention)
            logging.info(f'Issue Creation done with {r.status_code} code')
            return func.HttpResponse("Could not protect a branch.", status_code=200)
    else:
        return func.HttpResponse("We skipped the event. Only 'created' event is supported.", status_code=200)





