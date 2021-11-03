import logging
import azure.functions as func
import json
import metapy
import pytoml
from multiprocessing import Pool
import sharedcode.paragraph_ranker as ranker

#this async tag helps stop some threading issues with metapy
async def main(req: func.HttpRequest, context) -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')

    query = req.params.get('query')
    if not query:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            query = req_body.get('query')

    documentHtml = req.params.get('documentHtml')
    if not documentHtml:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            documentHtml = req_body.get('documentHtml')

    maxResults = req.params.get('maxResults')            
    if not maxResults:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            maxResults = req_body.get('maxResults')
    mode = req.params.get('mode')            
    if not mode:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            mode = req_body.get('mode')
    splitby = req.params.get('splitby')            
    if not splitby:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            splitby = req_body.get('splitby')   
    numelements = req.params.get('numelements')                      
    if not numelements:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            numelements = req_body.get('numelements')                                   

    if query and documentHtml:
        pr=ranker.ParagraphRanker()

        if not maxResults:
            maxResults = 10
        if not mode:
            mode = "pseudo"
        if not splitby:
            splitby = "."
        if not numelements:
            numelements=1

        #may need to reorganize this
        returnstring = pr.search(documentHtml,query,maxResults,mode,splitby,numelements)
        return func.HttpResponse(returnstring)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully, but invalid parameters were passed.",

             status_code=200
        )
