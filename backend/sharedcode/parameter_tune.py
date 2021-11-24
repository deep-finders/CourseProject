import numpy as np
import paragraph_ranker
import store_rankings
import pandas as pd
import json
import os

"""
  This logic was created to loop through different parameter values and look for the most optimal
  mode, k1, and b
"""

#precision calcs modified From https://gist.github.com/eribeiro/4630eb4b5562f38fd478d9694aa41ce2
def precision(docs):
    return sum(docs) / len(docs) if docs else 0

#avg precision = sum of precision at every document retrieved/number of relevant documents

def avg_precision(docs):
    vals_to_avg = [precision(docs[:i+1]) for (i, doc) in enumerate(docs) if doc == 1]

    return sum(vals_to_avg) / len(vals_to_avg) if vals_to_avg else 0


def run_test(test_set,top_n, mode, split_by, num_elements, k1, b, stem):
    map = 0
    ap_counter = 0
    count = 0
    pr = paragraph_ranker.ParagraphRanker()

    #for each test item
    for result in test_set:
        query = result["query"]
        raw_html = result["documentHtml"]
        results = result["results"]

        result_list = list()
        for result in results:
            if result["feedback"]=="1":
                passage = result["passage"]
                passage = passage.replace('\n',"")
                passage = passage.replace(split_by,"")                
                result_list.append(passage)


        try:
            new_results = pr.search(raw_html, query, top_n, mode, split_by, num_elements, k1, b, stem,store=False)
            new_results = json.loads(new_results)

            #now need to build a list of passages in new_results that are in results with feedback = 1
            found_list = list()

            max_idx = len(new_results) if top_n > len(new_results) else top_n

            for i in range(0,max_idx):

                passage = new_results[i]["passage"]
                passage = passage.replace('\n',"")
                passage = passage.replace(split_by,"")
                if passage in result_list:
                    found_list.append(1)
                else:
                    found_list.append(0)
            

            ap_counter = ap_counter + avg_precision(found_list)

            count = count+1
        except:
            print('Error calculating search')

    if count > 0:
        map = ap_counter/count

    return map


def main():
  
    # Default values
    top_n = 10
    split_by = '.'
    num_elements = 1
    stem = 'Y'

    #load the test data set
    dal = store_rankings.RankerDAL()
    testset = dal.get_testset()
    #this may have memory issues once dataset grows
    testset = list(testset)

    ##We'll vary b from 0 to 1 and k from 0 to 3 and for modes pseudo and tag
    bsplits = 10
    k1splits = 30

    tag_list = {'pseudo', 'tag'}
    b_list = np.linspace(0,1,bsplits)   
    b_list = np.round(b_list,2)
    k1_list = np.linspace(0,3,k1splits)
    k1_list = np.round(k1_list,2)

    num_tests = len(tag_list) * len(b_list) * len(k1_list)
    tests_executed = 0

    results_dict = {}
    for mode in tag_list:
        for b in b_list:
            for k1 in k1_list:
                results = run_test(testset,top_n, mode, split_by, num_elements, k1, b, stem)
                results_dict[(mode,b,k1)] = {'score':results}  
                tests_executed = tests_executed + 1
                print('*********** ' + str(tests_executed) + ' of ' + str(num_tests) + ' tests executed. ***********')

            
    # Show results
    df_results = pd.DataFrame(results_dict).T.reset_index()
    df_results.columns = ['mode','b','k1','score']
    df_results = df_results.sort_values(['score'],ascending=False)    
    print(df_results)
    try:
        os.remove("backend/sharedcode/output/results.csv")
    except:
        pass
    df_results.to_csv("backend/sharedcode/output/results.csv")


if __name__ == "__main__":
    main()

