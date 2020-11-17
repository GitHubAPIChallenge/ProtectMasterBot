import logging
import os
import json
import pprint
import requests 
import azure.functions as func

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

    # Read json parameters for rules and comment
    with open("config/protection_rules.json") as rule_file:
        branch_protection_rules = json.load(rule_file)
    with open("config/protection_comment.json") as comment_file:
        branch_protection_comment = json.load(comment_file)

    gh_client = GitHubClient(access_token, gh_org, gh_repo, gh_default_branch)

    if gh_event == 'created':
        try:
            # Protect repository
            r1 = ga_client.protect_repository(branch_protection_rules)
            logging.info('ProtectMasterBot successfully protected the repository with { r1.status.code } code')

            r2 = ga_client.create_issue(branch_protection_comment)
            logging.info('ProtectMasterBot successfully created an issue with { r2.status.code } code')


        except:
            # To Be Added the error handling
            pass

        else:
            # To Be Added the error handling
            pass

    return func.HttpResponse(f"{ gh_event } function executed successfully!", status_code=200)

