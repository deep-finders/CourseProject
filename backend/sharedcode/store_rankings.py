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
    #Cosmos DB has a 2MB limit.  We should put in Azure storage, but for the purposes of this
    #project, if it fails, we will remove the documentHtml and try again
    try:
      container.create_item(rankings,id)
    except:
      rankings["documentHtml"]=""
      container.create_item(rankings,id)

  
  def update_feedback(self,result_id,feedback):
    client = cosmos_client.CosmosClient(COSMOS_HOST, MASTER_KEY)
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(COLLECTION_ID)
    
    docs = container.query_items(query="SELECT c.id,c.results FROM c join r in c.results where r.id='"+ result_id + "'",enable_cross_partition_query=True)
    for doc in docs:
      for result in doc["results"]:
          if(result["id"]==result_id):
            result['feedback']=feedback
            container.upsert_item(doc)

  def get_testset(self):
    client = cosmos_client.CosmosClient(COSMOS_HOST, MASTER_KEY)
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(COLLECTION_ID)
    
    docs = container.query_items(query="Select c.query, c.documentHtml, c.results from c join r in c.results where c.documentHtml <> '' and r.feedback = '1'",enable_cross_partition_query=True)
    return docs
   