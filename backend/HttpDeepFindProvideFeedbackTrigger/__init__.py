import logging

import azure.functions as func
import sharedcode.store_rankings as store_rankings


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    result_id = req.params.get('id')
    if not result_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            result_id = req_body.get('result_id')
    feedback = req.params.get('feedback')
    if not feedback:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            feedback = req_body.get('feedback')

    if result_id and feedback:
        try:
            dal = store_rankings.RankerDAL()
            dal.update_feedback(result_id,feedback)
        except:
            logging.info('Error storing results in CosmosDB')
        return func.HttpResponse(f"Result updated function executed successfully.")
    else:
        return func.HttpResponse(
             "result_id and feedback must be passed.",
             status_code=200
        )
