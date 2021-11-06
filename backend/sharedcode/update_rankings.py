import os
import uuid
import json
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import pandas as pds


COSMOS_HOST = 'https://deepfinderdb.documents.azure.com:443/'
MASTER_KEY = 'suEVi72SUzWzIVB6n1IIU5PmZfZ5ZZbVLj7yO3pDZ41Avw36NmqeVU3Li4NUsNjWAqpovXHhJ9FvDtLFh1AWiw=='
DATABASE_ID = 'DeepFindQueries'
COLLECTION_ID = 'DeepFindContainer'
database_link = 'dbs/' + DATABASE_ID
collection_link = database_link + '/colls/' + COLLECTION_ID
# Use sample bulk SP from here: https://github.com/Azure/azure-cosmosdb-js-server/blob/master/samples/stored-procedures/BulkImport.js
sproc_link = collection_link + '/sprocs/bulkImport'


if __name__ == "__main__":
    result_id = "a2882b88-2bfe-47d4-a84c-9a07cb9cf596"
    feedback="1"
    client = cosmos_client.CosmosClient(COSMOS_HOST, MASTER_KEY)
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(COLLECTION_ID)
    
    docs = container.query_items(query="SELECT * FROM c where c.results[0].id='"+ result_id + "'",enable_cross_partition_query=True)
    for doc in docs:
      for result in doc["results"]:
          if(result["id"]==result_id):
            result['feedback']=feedback
            container.upsert_item(doc)


