from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from gensim.parsing.preprocessing import STOPWORDS
from rank_bm25 import *
import numpy as np
from goose3 import Goose
import sys
import json
import nltk
import uuid
import argparse
import os

#Note:  This try catch logic was added to allow the class to be used from the Azure function or from the 
#       main entry point
try:
    isfunction = os.environ["isfunction"]
except:
    isfunction = 'false'
if isfunction == 'true':
    import sharedcode.store_rankings as store_rankings
else:
    import store_rankings as store_rankings

import logging

"""
    This class is instantiated by the Azure function to allow the search to be executed
"""
class ParagraphRanker:
    def __init__(self):
        nltk.download('punkt')

    # Clean stopwords
    def remove_stopwords(self, paragraphs):
        sw_removed_paragraphs = list()
        for paragraph in paragraphs:
            paragraph_tokens = word_tokenize(paragraph)
            tokens_without_sw = [word for word in paragraph_tokens if word not in STOPWORDS]
            sw_removed_paragraph = ' '.join(tokens_without_sw)
            sw_removed_paragraphs.append(sw_removed_paragraph)

        return sw_removed_paragraphs

    # Stem paragraphs
    def stem_paragraphs(self, paragraphs):
        ps = PorterStemmer()
        stemmed_paragraphs = list()
        for paragraph in paragraphs:
            paragraph_tokens = word_tokenize(paragraph)
            stemmed_tokens = [ps.stem(word) for word in paragraph_tokens]
            stemmed_paragraph = ' '.join(stemmed_tokens)
            stemmed_paragraphs.append(stemmed_paragraph)

        return stemmed_paragraphs

    def stem_query(self, query):
        ps = PorterStemmer()
        query_tokens = word_tokenize(query)
        stemmed_tokens = [ps.stem(word) for word in query_tokens]
        return ' '.join(stemmed_tokens)

    # Remove empty paragraphs and new lines only paragraphs
    def remove_empty_paragraphs(self, paragraphs):
        cleaned_paragraphs = list()
        for paragraph in paragraphs:
            if paragraph == '' or paragraph == '\n':
                continue
            cleaned_paragraphs.append(paragraph)

        return np.array(cleaned_paragraphs)

    # Build paragraphs list based on raw html and mode
    def get_paragraphs(self, raw_html, mode, split_by, num_elements):
        paragraphs = []

        # Builds paragraphs from split article based on multiples of num_elements
        if mode == 'pseudo':

            # Retrieve the entire cleaned article
            logging.info('Calling goose with splityby="{}"'.format(split_by))
            g = Goose()
            article = g.extract(raw_html=raw_html)
            lines = article.cleaned_text.split(split_by)
            logging.info('Number of lines in pseudo mode: {}'.format(len(lines)))

            # Form paragraphs from multiples of num_elements
            i = 0
            while i < len(lines):
                paragraph = ''
                sentences = lines[i:i + num_elements]
                for sentence in sentences:
                    paragraph += sentence
                paragraphs.append(paragraph)
                i += num_elements

            return np.array(paragraphs)

        # Builds paragraphs from <p> and <td> tags found in the html
        elif mode == 'tag':
            soup = BeautifulSoup(raw_html, 'html.parser')

            # Get all <p> tags
            p_tags = soup.findAll('p')

            # Get all <td> tags
            td_tags = soup.findAll('td')

            # Get inner text of <p> and <td> tags to get list of paragraphs
            p_paragraphs = [tag.text for tag in p_tags]
            td_paragraphs = [tag.text for tag in td_tags]

            # Only include <td> paragraphs if available, only <p> paragraphs otherwise
            if len(td_paragraphs) > 0:
                paragraphs = p_paragraphs + td_paragraphs
            else:
                paragraphs = p_paragraphs

            return np.array(paragraphs)
    
    """
        This is a helper function to store the results for parameter tuning
    """
    def store_rankings(self, query, results, raw_html):
        # add a field to set the recommendation
        for result in results:
            result['feedback'] = '0'

        rankings = dict()
        rankings_id = str(uuid.uuid4())
        rankings["id"] = rankings_id
        rankings["query"] = query
        rankings["results"] = results
        rankings["documentHtml"] = raw_html

        try:
            dal = store_rankings.RankerDAL()
            dal.store_rankings(rankings_id, rankings)
        except:
            logging.info('Error storing results in CosmosDB')

    """
        This is a helper method to quickly remove some unwanted tags
    """
    def cleanpassage(self,passage):
        passage = passage.replace('\n',"")
        passage = passage.replace('\t',"")
        return passage

    """
        This is the main method that will parse the html and call the BM25 ranking function
    """
    def search(self, raw_html, query, top_n, mode, split_by, num_elements, k1, b, stem, store=True):

        # Save original query
        original_query = query

        # Build list of paragraphs
        paragraphs = self.get_paragraphs(raw_html, mode, split_by, num_elements)
        logging.info('Number of paragraphs after get_paragraphs: {}'.format(len(paragraphs)))     

        # Remove any empty paragraphs
        paragraphs = self.remove_empty_paragraphs(paragraphs)

        # clean up a couple parameters
        top_n = int(top_n)
        num_elements = int(num_elements)

        '''
        Observation: num_elements in pseudo mode should be adjusted such that 
        len(paragraphs) > n where n is the number of relevant paragraphs returned 
        by the ranker.
        '''
        print('Number of paragraphs: {}'.format(len(paragraphs)))
        logging.info('Number of paragraphs: {}'.format(len(paragraphs)))

        # Remove stop words from paragraphs
        paragraphs_clean = self.remove_stopwords(paragraphs)

        # Optional stem paragraphs, doesn't seem to always be an improvement
        if stem == 'Y' or stem == 'y':
            paragraphs_clean = self.stem_paragraphs(paragraphs_clean)
            query = self.stem_query(query)

        # Tokenize the corpus for BM25 model
        tokenized_corpus = [doc.split(' ') for doc in paragraphs_clean]

        results = list()

        # Initialize BM25 model, currently using default parameters k1=1.5, b=0.75
        logging.info("Before BM25 Call. k1={k1val} b={bval}".format(k1val=k1,bval=b))
        logging.info(tokenized_corpus)
        try:
            bm25 = BM25Okapi(tokenized_corpus, k1=k1, b=b)
            logging.info("After BM25 Call")
        
            # Tokenize query for BM25 retrieval
            tokenized_query = query.split()

            # Get scores for all paragraphs
            doc_scores = bm25.get_scores(tokenized_query)
            print('BM25 Scores:')
            print(doc_scores)

            # adjust top docs based on number of docs
            if len(tokenized_corpus) < top_n:
                top_n = len(tokenized_corpus)

            # Get the top n scores
            top_n_scores_idx = [score for score in reversed(np.argsort(doc_scores)[-top_n:])]

            # Get the top n paragraphs in their original form
            top_n_docs = paragraphs[top_n_scores_idx]

            # Print rank and paragraph
            print('Paragraph Rankings:')
            for idx, doc in enumerate(top_n_docs):
                #Removing results where BM25 score is 0
                if doc_scores[top_n_scores_idx[idx]] != 0:
                    doc_dict = {}
                    rank = idx + 1
                    doc_dict['id'] = str(uuid.uuid4())
                    doc_dict['rank'] = rank
                    doc_dict['score'] = doc_scores[top_n_scores_idx[idx]]
                    doc_dict['passage'] = self.cleanpassage(doc)
                    results.append(doc_dict)
                    print('Rank {}: '.format(rank) + doc)
        except Exception as e:
            logging.error(str(e))

        json_return = json.dumps(results)
        if store==True:
            self.store_rankings(original_query, results, raw_html)

        return json_return

    #This method will call both the pseudo mode and tag mode and return the best results
    def searchBoth(self, raw_html, query, top_n, split_by, num_elements, k1, b, stem, store=True):

            tag_results_orig = self.search(raw_html, query, top_n, "tag", split_by, num_elements, k1, b, stem,store=store)
            tag_results =  json.loads(tag_results_orig)
            psuedo_results_orig = self.search(raw_html, query, top_n, "pseudo", split_by, num_elements, k1, b, stem,store=store)
            psuedo_results =  json.loads(psuedo_results_orig)
            tag_score = 0
            psuedo_score = 0
            tag_result_found = False
            pseudo_result_found = False

            max_idx = len(tag_results) if top_n > len(tag_results) else top_n
            for i in range(0,max_idx):
                tag_result_found = True
                tag_score = tag_score + float(tag_results[i]['score'])

            max_idx = len(psuedo_results) if top_n > len(psuedo_results) else top_n
            for i in range(0,max_idx):
                pseudo_result_found = True
                psuedo_score = psuedo_score + float(psuedo_results[i]['score'])

            if tag_result_found == False:
                return psuedo_results_orig
            else:
                if tag_score > psuedo_score:
                    return tag_results_orig 
                else:
                    return psuedo_results_orig


"""
    This is not used by the azure functions but is a good way to test the algorithms outside of the cloud deployment
"""
def main():
    pr = ParagraphRanker()

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--raw_html', type=str, required=True,
                        help='The raw html to return paragraph rankings for')
    parser.add_argument('-q', '--query', type=str, required=True, help='The query to be searched')
    parser.add_argument('-t', '--top_n', type=int, help='The number of results returned in the ranking')
    parser.add_argument('-m', '--mode', type=str, help='The mode we build our paragraphs with (pseudo, tag).')
    parser.add_argument('-s', '--split_by', type=str,
                        help='Denotes how we split the text into sentences in pseudo mode')
    parser.add_argument('-n', '--num_elements', type=int, help='The number of sentences per pseudo paragraph')
    parser.add_argument('-k', '--k1', type=float, help='The k1 parameter of the BM25 ranker')
    parser.add_argument('-b', '--b', type=float, help='The b parameter of the BM25 ranker')
    parser.add_argument('-c', '--stem', type=str, help='Determines if the text is stemmed or not. Possible values: (Y, y, N,n)')

    args = vars(parser.parse_args())

    # Default values
    raw_html = ''
    query = ''
    top_n = 10
    mode = 'pseudo'
    split_by = '.'
    num_elements = 1
    k1 = 1.5
    b = 0.75
    stem = 'N'
    if args['raw_html']:
        raw_html = args['raw_html']
    if args['query']:
        query = args['query']
    if args['top_n']:
        top_n = args['top_n']
    if args['mode']:
        if args['mode'] == 'pseudo' or args['mode'] == 'tag':
            mode = args['mode']
        else:
            print('Error: mode must be pseudo or tag')
            sys.exit(-1)
    if args['split_by']:
        split_by = args['split_by']
    if args['num_elements']:
        num_elements = args['num_elements']
    if args['k1']:
        k1 = args['k1']
    if args['b']:
        b = args['b']
    if args['stem'] == 'Y' or args['stem'] == 'y':
        stem = args['stem']

    return pr.search(raw_html, query, top_n, mode, split_by, num_elements, k1, b, stem)


if __name__ == "__main__":
    main()
