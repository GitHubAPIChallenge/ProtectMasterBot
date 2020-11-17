import logging
import os
import json
import base64
import azure.functions as func
from azure.cosmos import CosmosClient
import lib.password_client as password_client



def main(req: func.HttpRequest, outdoc: func.Out[func.Document])  -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')

    password = req.form['password']
    org = req.form['org']
    rules = req.form['rules']
    mention = req.form['mention']

    conn_str = os.environ['cosmosdb_connection_string']
    client = CosmosClient.from_connection_string(conn_str, credential=None)
    database_name = "apichallenge"
    database = client.get_database_client(database_name)
    container_name = "usersettings"
    container = database.get_container_client(container_name)
    cosmos_query = f'SELECT * FROM c WHERE c.id="{ org }"'

    items = []
    for item in container.query_items(
            query=cosmos_query,
            enable_cross_partition_query=True):
        items.append(item)

    existing_data = items[0]
    validated = password_client.validate_password(password, existing_data["password_hash"])

    if validated:
        outdata = {
            "id": existing_data["id"],
            "installation_id": existing_data["installation_id"],
            "protection_json": rules,
            "mention": mention,
            "password_hash": existing_data["password_hash"]
        }
        outdoc.set(func.Document.from_json(json.dumps(outdata)))
        return func.HttpResponse(f"Success!", status_code=200)
    else:
        return func.HttpResponse(f"Update Failure", status_code=500)




