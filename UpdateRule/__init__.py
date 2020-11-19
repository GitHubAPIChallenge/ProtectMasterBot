import logging
import os
import json
import base64
import azure.functions as func
from azure.cosmos import CosmosClient
from jsonschema import validate, ValidationError
import lib.password_client as password_client
from lib import cosmosdb_client

# ---------------------------------------------------------
# 
#  This is a main function for updating protection rules in CosmosDB
# 
# ---------------------------------------------------------

def main(req: func.HttpRequest, outdoc: func.Out[func.Document])  -> func.HttpResponse:

    logging.info('ProtectMasterBot is now updating data in CosmosDB')

    # Get and set params from the request
    try: 
        password = req.form['password']
        gh_org = req.form['org']
        user_rules = req.form['rules']
        mention = req.form['mention']
    except (KeyError, ValueError):  
        logging.error('Json payload was not valid')
        return func.HttpResponse("Sorry, something went wrong!", status_code=500)


    # Get and set params from environment variables
    try:
        connection_string = os.environ['cosmosdb_connection_string']
    except (KeyError, ValueError):
        logging.error('Could not read environment variables')
        return func.HttpResponse("Sorry, something went wrong!", status_code=500)

    # Get org data from CosmosDB
    try:
        cc = cosmosdb_client.CosmosDBClient(connection_string, "apichallenge", "usersettings")
        existing_data = cc.get(gh_org)
    except: 
        return func.HttpResponse("Sorry, something went wrong!", status_code=500)

    password_validation = password_client.validate_password(password, existing_data["password_hash"])

    if password_validation:
        try: 
            outdata = {
                "id": existing_data["id"],
                "installation_id": existing_data["installation_id"],
                "protection_json": user_rules,
                "mention": mention,
                "password_hash": existing_data["password_hash"]
            }
            outdoc.set(func.Document.from_json(json.dumps(outdata)))
            return func.HttpResponse(f"Success!", status_code=200)
        except:
            logging.error('Could not store data in CosmosDB')
            return func.HttpResponse("2Sorry, something went wrong!", status_code=500)
    else:
        return func.HttpResponse(f"You gave me a wrong password.", status_code=500)




