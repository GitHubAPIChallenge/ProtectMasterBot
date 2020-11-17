import logging
import pprint
import json
import requests 
import os

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ProtectMasterBot caught GitHub repository event.')

    name = req.params.get('body')

    request_body = json.loads(req.get_body())
    gh_event = request_body['action']
    gh_org = request_body['organization']['login']
    gh_repo = request_body['repository']['name']
    gh_default_branch = request_body['repository']['default_branch']
    access_token = os.environ["gh_access_token"]

    with open("protection_rules.json") as rule_file:
        branch_protection_rules = json.load(rule_file)
    
    with open("protection_comment.json") as comment_file:
        branch_protection_comment = json.load(comment_file)

    if gh_event == 'created':
        try:
            # Protect repository
            r = requests.put(
                f"https://api.github.com/repos/{ gh_org }/{ gh_repo }/branches/{ gh_default_branch }/protection",
                headers = {
                    'Accept': 'application/vnd.github.luke-cage-preview+json',
                    'Authorization': f"Token { access_token }"
                },
                json = branch_protection_rules
            )
            logging.info('ProtectMasterBot successfully protected the repository with { r.status.code } code')
            logging.info(r.json())
        except:
            # To Be Added the error handling
            pass
        else:
            r = requests.post(
                f"https://api.github.com/repos/{ gh_org }/{ gh_repo }/issues",
                headers = {
                    'Accept': 'application/vnd.github.squirrel-girl-preview',
                    'Authorization': f"Token { access_token }"
                },
                json = branch_protection_comment
            )
            logging.info('ProtectMasterBot successfully created an issue with { r.status.code } code')
            print(r.json())

    return func.HttpResponse(f"{ gh_event } function executed successfully!", status_code=200)

