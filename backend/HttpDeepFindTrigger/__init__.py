"""
    This Azure function provides the ability to pass html text and call our ranker
    function to provde topN results
"""
import logging
import azure.functions as func
import json
import metapy
import pytoml
from multiprocessing import Pool
import sharedcode.paragraph_ranker as ranker

def main(req: func.HttpRequest, context) -> func.HttpResponse:

    try:
        req_body = req.get_json()
    except:
        return func.HttpResponse(
             "Error parsing the request body.",
             status_code=500
        )
    """
        query and documentHtml are required paramaters
        maxResults (TopN) is defaulted to 10
        mode is defaulted with "both".  This will run the query in both the tag (i.e. broken up by html) 
          or pseudo (i.e. stripped of html and broken up by sentences)
        k1 and b are parameters passed to BM25
        stem is defaulted to Y which causes both the query and text to be stemmed
    """

    query = req_body.get('query')
    documentHtml = req_body.get('documentHtml')
    maxResults = req_body.get('maxResults')
    if maxResults:
        maxResults = int(maxResults)    
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
            """
            Call the appropriate paragraph ranker method
             searchBoth will compare the results of both modes (pseudo/tag)
             search requires a mode be passed
            """
            if mode == "both":
                logging.info("Before Both Call")
                returnstring = pr.searchBoth(documentHtml,query,maxResults,splitby,numelements,k1,b,stem)
                logging.info("After Both Call")
            else:
                logging.info("Before " + mode + " Call")
                returnstring = pr.search(documentHtml,query,maxResults,mode,splitby,numelements,k1,b,stem)
                logging.info("After " + mode + " Call")
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
