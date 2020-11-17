import logging
import os
import json
import pprint
import requests 
import azure.functions as func

from azure.cosmos import CosmosClient
from jsonschema import validate, ValidationError

from lib import github_client
from lib import github_token_client

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('ProtectMasterBot caught GitHub repository event.')

    # Get and set params from the request
    request_body = json.loads(req.get_body())
    gh_event = request_body['action']
    gh_org = request_body['organization']['login']
    gh_repo = request_body['repository']['name']
    gh_default_branch = request_body['repository']['default_branch']

    # まず、InstallationID をゲット

    conn_str = os.environ['cosmosdb_connection_string']

    client = CosmosClient.from_connection_string(conn_str, credential=None)
    database_name = "apichallenge"
    database = client.get_database_client(database_name)
    container_name = "usersettings"
    container = database.get_container_client(container_name)
    cosmos_query = f'SELECT * FROM c WHERE c.id="{ gh_org }"'

    items = []
    for item in container.query_items(
            query=cosmos_query,
            enable_cross_partition_query=True):
        items.append(item)

    installation_id = items[0]["installation_id"]
    protection_json = items[0]["protection_json"]
    mention = items[0]["mention"]

    # Token を払い出す。
    app_id = os.environ["gh_app_id"]
    app_pem = os.environ["gh_app_pem"]
    gh_token_client = github_token_client.GitHubTokenClient(app_id, app_pem, installation_id)
    access_token = gh_token_client.get_token()




    # Read protection rules json parameters
    try:
        with open("config/protection_rules.json") as rule_file:
            branch_protection_rules = json.load(rule_file)
        with open('config/protection_rules_schema.json') as schema_file:
            rules_schema = json.load(schema_file)
        validate(branch_protection_rules, rules_schema)
    except ValidationError as e:
        logging.info('Validation Error on protection_rules.json')

    gh_client = github_client.GitHubClient(access_token, gh_org, gh_repo, gh_default_branch)
    # Initial Commit として Master に README.md を追加
    print(protection_json)
    if len(protection_json) > 0:
        branch_protection_rules = json.loads(protection_json)

    if gh_event == 'created':
        # Create README.md
        gh_client.create_readme()

        # Protect Repository
        code = gh_client.protect_repository(branch_protection_rules)

        if code == 200:
            # Create an Issue
            gh_client.create_issue(branch_protection_rules, mention)
        else:
            gh_client.create_failure_issue(mention)


    return func.HttpResponse(f"{ gh_event } function executed successfully!", status_code=200)

