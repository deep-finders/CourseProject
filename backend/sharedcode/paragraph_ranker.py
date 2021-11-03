from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from gensim.parsing.preprocessing import STOPWORDS
from rank_bm25 import *
import numpy as np
from goose3 import Goose
import sys
import json
import argparse


# Clean stopwords
def remove_stopwords(paragraphs):
    sw_removed_paragraphs = list()
    for paragraph in paragraphs:
        paragraph_tokens = word_tokenize(paragraph)
        tokens_without_sw = [word for word in paragraph_tokens if word not in STOPWORDS]
        sw_removed_paragraph = ' '.join(tokens_without_sw)
        sw_removed_paragraphs.append(sw_removed_paragraph)

    return sw_removed_paragraphs


# Stem paragraphs
def stem_paragraphs(paragraphs):
    ps = PorterStemmer()
    stemmed_paragraphs = list()
    for paragraph in paragraphs:
        paragraph_tokens = word_tokenize(paragraph)
        stemmed_tokens = [ps.stem(word) for word in paragraph_tokens]
        stemmed_paragraph = ' '.join(stemmed_tokens)
        stemmed_paragraphs.append(stemmed_paragraph)

    return stemmed_paragraphs


# Remove empty paragraphs and new lines only paragraphs
def remove_empty_paragraphs(paragraphs):
    cleaned_paragraphs = list()
    for paragraph in paragraphs:
        if paragraph == '' or paragraph == '\n':
            continue
        cleaned_paragraphs.append(paragraph)

    return np.array(cleaned_paragraphs)


# Build paragraphs list based on raw html and mode
def get_paragraphs(raw_html, mode, split_by, num_elements):
    paragraphs = []

    # Builds paragraphs from split article based on multiples of num_elements
    if mode == 'pseudo':

        # Retrieve the entire cleaned article
        g = Goose()
        article = g.extract(raw_html=raw_html)
        # article = g.extract(raw_html=raw_html)
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


if __name__ == "__main__":

    # Read command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--raw_html', type=str, required=True,
                        help='The raw html to return paragraph rankings for')
    parser.add_argument('-q', '--query', type=str, required=True, help='The query to be searched')
    parser.add_argument('-t', '--top_n', type=int, help='The number of results returned in the ranking')
    parser.add_argument('-m', '--mode', type=str, help='The mode we build our paragraphs with (pseudo, tag).')
    parser.add_argument('-s', '--split_by', type=str,
                        help='Denotes how we split the text into sentences in pseudo mode')
    parser.add_argument('-n', '--num_elements', type=int, help='The number of sentences per pseudo paragraph')

    args = vars(parser.parse_args())

    # Default values
    raw_html = ''
    query = ''
    top_n = 10
    mode = 'pseudo'
    split_by = '.'
    num_elements = 1

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

    # Build list of paragraphs
    paragraphs = get_paragraphs(raw_html, mode=mode, split_by=split_by, num_elements=num_elements)
    # Remove any empty paragraphs
    paragraphs = remove_empty_paragraphs(paragraphs)

    '''
    Observation: num_elements in pseudo mode should be adjusted such that 
    len(paragraphs) > n where n is the number of relevant paragraphs returned 
    by the ranker.
    '''
    print('Number of paragraphs: {}'.format(len(paragraphs)))

    # Remove stop words from paragraphs
    paragraphs_clean = remove_stopwords(paragraphs)

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

    # Get the top n scores
    top_n_scores_idx = [score for score in reversed(np.argsort(doc_scores)[-top_n:])]

    # Get the top n paragraphs in their original form
    top_n_docs = paragraphs[top_n_scores_idx]

    results = []

    # Print rank and paragraph
    print('Paragraph Rankings:')
    for idx, doc in enumerate(top_n_docs):
        doc_dict = {}
        rank = idx + 1
        doc_dict['rank'] = rank
        doc_dict['score'] = doc_scores[top_n_scores_idx[idx]]
        doc_dict['passage'] = doc
        results.append(doc_dict)
        print('Rank {}: '.format(rank) + doc)

    # Create json result and write to output file
    json_return = json.dumps(results)

    with open('output/ranking_result.json', 'w') as file:
        json.dump(json_return, file)