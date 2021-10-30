import logging
import azure.functions as func
import json
import metapy
import pytoml

import sharedcode.ranker as ranker

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    query = req.params.get('query')
    if not query:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            query = req_body.get('query')

    passages = req.params.get('passages')
    if not passages:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            passages = req_body.get('passages')

    rk = ranker.PassageRanker(query,passages)

    if query and len(passages)>0:
        returnstring = rk.process()
        return func.HttpResponse(returnstring)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully, but invalid parameters were passed. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
