import logging
import azure.functions as func
import json
import metapy
import pytoml
from multiprocessing import Pool
import sharedcode.ranker as ranker

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

    if query and documentHtml:
        rk = ranker.PassageRanker(query,documentHtml,context)

        returnstring = rk.process()
        return func.HttpResponse(returnstring)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully, but invalid parameters were passed.",

             status_code=200
        )
