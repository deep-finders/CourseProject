import logging
import azure.functions as func
import json
import metapy
import pytoml
from multiprocessing import Pool
import sharedcode.paragraph_ranker as ranker

#this async tag helps stop some threading issues with metapy
async def main(req: func.HttpRequest, context) -> func.HttpResponse:

    try:
        req_body = req.get_json()
    except:
        return func.HttpResponse(
             "Error parsing the request body.",
             status_code=500
        )

    query = req_body.get('query')
    documentHtml = req_body.get('documentHtml')
    maxResults = req_body.get('maxResults')
    mode = req_body.get('mode')
    splitby = req_body.get('splitby')   
    numelements = req_body.get('numelements')       
    if numelements:
        numelements= int(numelements)                            
    k1 = req_body.get('k1')
    if k1:
        k1 = float(k1)
    b = req_body.get('b')
    if b:
        b = float(b)            
    stem = req_body.get('stem')

    if query and documentHtml:
        pr=ranker.ParagraphRanker()

        if not maxResults:
            maxResults = 10
        if not mode:
            mode = "both"
        if not splitby:
            splitby = "."
        if not numelements:
            numelements=1
        if not k1:
            k1=1.5
        if not b:
            b=.75
        if not stem:
            stem  = "Y"

        try:
            if mode == "both":
                returnstring = pr.searchBoth(documentHtml,query,maxResults,splitby,numelements,k1,b,stem)
            else:
                returnstring = pr.search(documentHtml,query,maxResults,mode,splitby,numelements,k1,b,stem)
            statuscode = 200
        except Exception as e:
            returnstring = str(e)
            statuscode = 500
        
        return func.HttpResponse(returnstring, status_code=statuscode)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully, but invalid parameters were passed.",
             status_code=500
        )
