from bs4 import BeautifulSoup
import urllib.request
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from gensim.parsing.preprocessing import STOPWORDS
from rank_bm25 import *
import numpy as np
from goose3 import Goose


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


# Build paragraphs list based on url and mode
def get_paragraphs(url, mode='pseudo', split_by='.', num_elements=3):
    paragraphs = []

    # Builds paragraphs from split article based on multiples of num_elements
    if mode == 'pseudo':

        # Retrieve the entire cleaned article
        g = Goose()
        article = g.extract(url=url)
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
        source = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(source, 'html.parser')

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
    # Url of page
    # url = 'https://en.wikipedia.org/wiki/Squid_Game'
    url = 'https://www.pcgamer.com/facebook-new-name-meta/'

    paragraphs = get_paragraphs(url, mode='tag')
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

    # Query for retrieval
    # query = 'prize money'
    # query = 'dalgona'
    query = 'why new name?'

    # Tokenize query for BM25 retrieval
    tokenized_query = query.split()

    # Get scores for all paragraphs
    doc_scores = bm25.get_scores(tokenized_query)
    print('BM25 Scores:')
    print(doc_scores)

    # N for top n paragraphs to be retrieved
    n = 5

    # Get the top n scores
    top_n_scores_idx = [score for score in reversed(np.argsort(doc_scores)[-n:])]

    # Get the top n paragraphs in their original form
    top_n_docs = paragraphs[top_n_scores_idx]

    # Print rank and paragraph
    print('Paragraph Rankings:')
    for idx, doc in enumerate(top_n_docs):
        print('Rank {}: '.format(idx + 1) + doc)