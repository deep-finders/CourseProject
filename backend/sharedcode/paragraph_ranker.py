from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from gensim.parsing.preprocessing import STOPWORDS
from rank_bm25 import *
import numpy as np
from goose3 import Goose
import sys
import getopt
import json
import nltk
import uuid

class ParagraphRanker:
    def __init__(self):
        nltk.download('punkt')
    
    # Clean stopwords
    def remove_stopwords(self,paragraphs):
        sw_removed_paragraphs = list()
        for paragraph in paragraphs:
            paragraph_tokens = word_tokenize(paragraph)
            tokens_without_sw = [word for word in paragraph_tokens if word not in STOPWORDS]
            sw_removed_paragraph = ' '.join(tokens_without_sw)
            sw_removed_paragraphs.append(sw_removed_paragraph)

        return sw_removed_paragraphs


    # Stem paragraphs
    def stem_paragraphs(self,paragraphs):
        ps = PorterStemmer()
        stemmed_paragraphs = list()
        for paragraph in paragraphs:
            paragraph_tokens = word_tokenize(paragraph)
            stemmed_tokens = [ps.stem(word) for word in paragraph_tokens]
            stemmed_paragraph = ' '.join(stemmed_tokens)
            stemmed_paragraphs.append(stemmed_paragraph)

        return stemmed_paragraphs


    # Remove empty paragraphs and new lines only paragraphs
    def remove_empty_paragraphs(self,paragraphs):
        cleaned_paragraphs = list()
        for paragraph in paragraphs:
            if paragraph == '' or paragraph == '\n':
                continue
            cleaned_paragraphs.append(paragraph)

        return np.array(cleaned_paragraphs)


    # Build paragraphs list based on raw html and mode
    def get_paragraphs(self,raw_html, mode, split_by, num_elements):
        paragraphs = []

        # Builds paragraphs from split article based on multiples of num_elements
        if mode == 'pseudo':

            # Retrieve the entire cleaned article
            g = Goose()
            article = g.extract(raw_html=raw_html)
            lines = article.cleaned_text.split(split_by)

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
    
    def search(self,raw_html,query,top_n,mode,split_by,num_elements):

        # Build list of paragraphs
        paragraphs = self.get_paragraphs(raw_html, mode, split_by, num_elements)
        # Remove any empty paragraphs
        paragraphs = self.remove_empty_paragraphs(paragraphs)

        #clean up a couple parameters
        top_n = int(top_n)
        num_elements = int(num_elements)

        '''
        Observation: num_elements in pseudo mode should be adjusted such that 
        len(paragraphs) > n where n is the number of relevant paragraphs returned 
        by the ranker.
        '''
        print('Number of paragraphs: {}'.format(len(paragraphs)))

        # Remove stop words from paragraphs
        paragraphs_clean = self.remove_stopwords(paragraphs)

        # Optional stem paragraphs, doesn't seem to always be an improvement
        # paragraphs_clean = stem_paragraphs(paragraphs_clean)

        # Tokenize the corpus for BM25 model
        tokenized_corpus = [doc.split(' ') for doc in paragraphs_clean]

        # Initialize BM25 model, currently using default parameters k1=1.5, b=0.75
        bm25 = BM25Okapi(tokenized_corpus)

        print("Query: {}".format(query))
        print("Num_Elements: {}".format(num_elements))
        print("Top N: {}".format(top_n))
        print("Mode: {}".format(mode))
        print("Split_By: {}".format(split_by))

        # Tokenize query for BM25 retrieval
        tokenized_query = query.split()

        # Get scores for all paragraphs
        doc_scores = bm25.get_scores(tokenized_query)
        print('BM25 Scores:')
        print(doc_scores)

        # adjust top docs based on number of docs
        if len(tokenized_corpus)<top_n:
            top_n=len(tokenized_corpus)

        # Get the top n scores
        top_n_scores_idx = [score for score in reversed(np.argsort(doc_scores)[-top_n:])]

        # Get the top n paragraphs in their original form
        top_n_docs = paragraphs[top_n_scores_idx]

        results = list()

        # Print rank and paragraph
        print('Paragraph Rankings:')
        for idx, doc in enumerate(top_n_docs):
            doc_dict = {}
            rank = idx + 1
            doc_dict['id'] = str(uuid.uuid4())
            doc_dict['rank'] = rank
            doc_dict['score'] = doc_scores[top_n_scores_idx[idx]]
            doc_dict['passage'] = doc
            if  doc_dict['score']>0:
                results.append(doc_dict)
            print('Rank {}: '.format(rank) + doc)

        json_return = json.dumps(results)
        print(json_return)
        return json_return


def main(argv):
    pr=ParagraphRanker()

    # Read Command Line Arguments
    if len(argv) < 2:
        print('-r or --raw_html and -q or --query required')
        print('./paragraph_ranker -r <raw_html> -q <query> -t [top_n] -m [mode] -s [split_by] -n [num_elements]')
        sys.exit(-1)

    options = "hr:q:t:m:s:n:"
    long_options = ['help', 'raw_html = ', 'query =', 'top_n =', 'mode =', 'split_by =', 'num_elements =']

    raw_html = ''
    query = ''
    top_n = 10
    mode = 'pseudo'
    split_by = '.'
    num_elements = 1

    try:
        args, values = getopt.getopt(argv, options, long_options)

        for curr_arg, curr_val in args:
            if curr_arg in ('-h', '--help'):
                print('./paragraph_ranker -r <raw_html> -q <query> -t [top_n] -m [mode] -s [split_by] -n [num_elements]')
                sys.exit(2)
            elif curr_arg in ('-r', '--raw_html'):
                raw_html = curr_val
            elif curr_arg in ('-q', '--query'):
                query = curr_val
            elif curr_arg in ('-t', '--top_n'):
                top_n = int(curr_val)
            elif curr_arg in ('-m', '--mode'):
                mode = curr_val
            elif curr_arg in ('-s', '--split_by'):
                split_by = curr_val
            elif curr_arg in ('-n', '--num_elements'):
                num_elements = int(curr_val)

    except getopt.error as err:
        print(str(err))

    return pr.search(raw_html,query,top_n,mode,split_by,num_elements)
 

if __name__ == "__main__":
    main(sys.argv[1:])