import logging
from azure.cosmos import CosmosClient

# ---------------------------------------------------------
# 
#  This is a wrapper class of CosmosDB Client
# 
# ---------------------------------------------------------

class CosmosDBClient:
    def __init__(self, connection_string, database_name, container_name):
        self.connection_string = connection_string
        self.database_name = database_name
        self.container_name = container_name
        self.client = CosmosClient.from_connection_string(self.connection_string, credential=None)
    
    # Get data tied to specific organization
    def get(self, org):
        try: 
            database = self.client.get_database_client(self.database_name) 
            container = database.get_container_client(self.container_name)
            items = []
            for item in container.query_items(
                query = f'SELECT * FROM c WHERE c.id="{ org }"',
                enable_cross_partition_query = True):
                items.append(item)
            return items[0]
        except:
            logging.error("Error! CosmosDB Client couldn't get the result.")
            raise
