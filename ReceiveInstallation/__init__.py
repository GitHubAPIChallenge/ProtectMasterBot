import os
import json
import sys

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

            # 必要な情報を登録する
            gh_org = gh_token_client.get_installation()

            credentials = gh_token_client.generate_password()
            password = credentials["password"]
            hash = credentials["hash"]

            # cosmosdb 
            outdata = {
                "gh_org": gh_org,
                "installation_id": installation_id,
                "protection_json": "",
                "mention": "",
                "password_hash": hash
            }

            outdoc.set(func.Document.from_json(json.dumps(outdata)))

        except: 
            logging.info(sys.exc_info())
            return func.HttpResponse(
                "Not Successful",
                status_code=500
            )
        else:
            return func.HttpResponse(
                f"""
                <html>
                <body>
                    <center>
                    <h1>The master protection is applied to your organization "{ gh_org }".</h1>
                    <h1>Please note the below password to configure setting.</h1>
                    <h1>Password: { password }</h1>
                    </center>
                </body>
                </html>
                """,
                status_code=200,
                headers={
                    "Content-Type": "text/html"
                }
            )


    else:
        return func.HttpResponse(
            "Not Successful",
            status_code=500
        )
