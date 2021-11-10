import os
import uuid
import json
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors

COSMOS_HOST = 'https://deepfinderdb.documents.azure.com:443/'
MASTER_KEY = os.environ['cosmoskey']
DATABASE_ID = 'DeepFindQueries'
COLLECTION_ID = 'DeepFindContainer'
database_link = 'dbs/' + DATABASE_ID
collection_link = database_link + '/colls/' + COLLECTION_ID
# Use sample bulk SP from here: https://github.com/Azure/azure-cosmosdb-js-server/blob/master/samples/stored-procedures/BulkImport.js
sproc_link = collection_link + '/sprocs/bulkImport'

class RankerDAL:

  def store_rankings(self,id,rankings):
    client = cosmos_client.CosmosClient(COSMOS_HOST, MASTER_KEY)
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(COLLECTION_ID)
    container.create_item(rankings,id)
  
  def update_feedback(self,result_id,feedback):
    client = cosmos_client.CosmosClient(COSMOS_HOST, MASTER_KEY)
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(COLLECTION_ID)
    
    docs = container.query_items(query="SELECT * FROM c where c.results[0].id='"+ result_id + "'",enable_cross_partition_query=True)
    for doc in docs:
      for result in doc["results"]:
          if(result["id"]==result_id):
            result['feedback']=feedback
            container.upsert_item(doc)