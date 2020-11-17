import os
import json

# Azure Function Related Library
import logging
import azure.functions as func

# Common Library
from lib import github_token_client

def main(req: func.HttpRequest, outdoc: func.Out[func.Document]) -> func.HttpResponse:
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
        try: 
            app_id = os.environ["gh_app_id"]
            app_pem = os.environ["gh_app_pem"]
            gh_token_client = github_token_client.GitHubTokenClient(app_id, app_pem, installation_id)

            token = gh_token_client.get_token()

            # cosmosdb 
            outdata = {"token": token}
            outdoc.set(func.Document.from_json(json.dumps(outdata)))

        except: 
            logging.info(sys.exc_info())
            return func.HttpResponse(
                "Not Successful",
                status_code=500
            )
        else:
            return func.HttpResponse(
                f"Your token is { token } !",
                status_code=200
            )


    else:
        return func.HttpResponse(
            "Not Successful",
            status_code=500
        )
