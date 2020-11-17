import os

# Azure Function Related Library
import logging
import azure.functions as func

# Common Library
from lib import github_token_client

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    installation_id = req.params.get('installation_id')
    if not installation_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            installation_id = req_body.get('installation_id')

    if installation_id:
        app_id = os.environ["gh_app_id"]
        app_pem = os.environ["gh_app_pem"]
        gh_token_client = github_token_client.GitHubTokenClient(app_id, app_pem, installation_id)

        token = gh_token_client.get_token()

        return func.HttpResponse(f"Your token is { token }. This HTTP triggered function executed successfully.")

    else:
        return func.HttpResponse(
            "Not Successful",
            status_code=500
        )
