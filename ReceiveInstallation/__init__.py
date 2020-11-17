import os
import json
import sys

# Azure Function Related Library
import logging
import azure.functions as func
import lib.password_client as password_client

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

            credentials = password_client.generate_password()
            password = credentials["password"]
            hash = credentials["hash"]

            # cosmosdb 
            outdata = {
                "id": gh_org,
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
                <head>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
                </head>
                <body>
                    <center>
                <div style="font-size:17px;max-width:800px;margin:40px auto;">
                        <h1>ProtectMasterBot</h1>
                        <h4>The branch protection is applied to your organization <strong>"{ gh_org }"</strong>.</h4>
                        <p>Please note the below password to configure setting. </p>
                        <p>The password is only shown here <strong>ONCE</strong>.</p>
                        <p>DO NOT share this password with others.</p>
                        <div style="background-color:#efefef;border-radius:5px;padding:10px;width:600px;">
                            <h4>Password: { password }</h4>
                        </div>
                        <hr>
                        <a href="/api/EditRule?org={gh_org}&password={password}"><div class="btn btn-primary"> Go To Setting </div></a> 
                </div>
                    </center>
                <body>
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
