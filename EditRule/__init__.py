import logging

import azure.functions as func
from lib import github_token_client
import lib.password_client as password_client

def main(req: func.HttpRequest, indoc: func.DocumentList) -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')

    password = req.params.get('password')
    org = req.params.get('org')
    password_hash = indoc[0]["password_hash"]
    rules = indoc[0]["protection_json"]
    mention = indoc[0]["mention"]
    with open("config/protection_rules.json") as rule_file:
        branch_protection_rules = rule_file.read()

    validated = password_client.validate_password(password, password_hash)
    if validated:
        return func.HttpResponse( f"""
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
                        <form action="/api/UpdateRule" method="POST">
                        <hr>
  <div class="form-group">
    <label >@Mention</label>
    <small id="formHelp" class="form-text text-muted">Who do you want to mention when the protection rule is applied?</small>
    <br>
    <input class="form-control" id="mention" name="mention" type="text" placeholder="@yuhattor, @foobar, @octcat">
    <small id="formHelp" class="form-text text-muted">Please list them separated by commas</small>
  </div>
                        <hr>
    <div class="form-group">
    <label>Protection Rule</label>
    <textarea class="form-control" name="rules" id="rule" rows="30">{ branch_protection_rules }</textarea>
  </div>

   <input type="hidden" id="org" name="org" value="{org}">
   <input type="hidden" id="password" name="password" value="{password}">
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
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
        return func.HttpResponse("Sorry, your org name and password don't match.", status_code=200)
    
    
