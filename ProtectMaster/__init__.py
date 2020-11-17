import logging
import os
import sys
import json
import pprint
import requests 
import azure.functions as func

from pathlib import Path
from jsonschema import validate, ValidationError

sys.path.append((Path(__file__).parent.parent).as_posix())
from lib.github_client import GitHubClient

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('ProtectMasterBot caught GitHub repository event.')

    # Get and set params from the request
    request_body = json.loads(req.get_body())
    gh_event = request_body['action']
    gh_org = request_body['organization']['login']
    gh_repo = request_body['repository']['name']
    gh_default_branch = request_body['repository']['default_branch']

    # Read environment variables
    access_token = os.environ["gh_access_token"]


    # Read protection rules json parameters
    try:
        with open("config/protection_rules.json") as rule_file:
            branch_protection_rules = json.load(rule_file)
        with open('config/protection_rules_schema.json') as schema_file:
            rules_schema = json.load(schema_file)
        validate(branch_protection_rules, rules_schema)
    except ValidationError as e:
        logging.info('Validation Error on protection_rules.json')

    gh_client = GitHubClient(access_token, gh_org, gh_repo, gh_default_branch)

    gh_client.generate_issue(branch_protection_rules)

    if gh_event == 'created':
        # Protect Repository
        gh_client.protect_repository(branch_protection_rules)

        # Create an Issue
        gh_client.create_issue(branch_protection_rules)


        try:
            pass

        except:
            # To Be Added the error handling
            pass

        else:
            # To Be Added the error handling
            pass

    return func.HttpResponse(f"{ gh_event } function executed successfully!", status_code=200)

