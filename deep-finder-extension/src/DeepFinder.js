/* eslint-disable no-undef */
import React, { useCallback, useEffect, useRef, useState } from 'react';

import './App.css';
import ResultsList from './components/ResultsList';
import SearchForm from './components/SearchForm';
import { search } from './services/searchService';

// Constants
const portName = 'deep-finder';

// Content Script Actions
const SEND_PAGE = 'send_page';
const PASSAGE_FOUND = 'passage_found';

// Extension Actions
const CLEAR_HIGHLIGHTS = 'clear_highlights';
const FIND_PASSAGES = 'find_passages';
const REQUEST_PAGE = 'request_page';
const SELECT_RESULT = 'select_result';

const DeepFinder = () => {

  const foundPassages = useRef([]);
  const port = useRef();

  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [visibleSearchResults, setVisibleSearchResults] = useState([]);
  const [selectedPassageRank, setSelectedPassageRank] = useState();

  const handleDocumentTextRetrieved = useCallback(async ({
    documentHtml,
    documentText,
    documentPTags,
    pageUrl,
    query,
  }) => {
    try {
      const results = await search({
        documentHtml,
        documentText,
        documentPTags,
        pageUrl,
        query,
      })
      setSearchResults(results);
      setIsLoading(false);
    } catch(e) {
      console.error(e);
      setIsLoading(false);
    }
  }, [])

  useEffect(() => {
    if (port?.current?.name === portName) {
      return;
    }

    const chromeMessageListener = ({ action, payload}) => {
      console.info('Handling message:', { action, payload });

      switch (action) {
        case PASSAGE_FOUND: {
          foundPassages.current.push(payload);
          setVisibleSearchResults([...foundPassages.current]);
          break;
        }

        case SEND_PAGE: {
          handleDocumentTextRetrieved({ ...payload })
          break;
        }

        default:
          return;
      }
    }

    async function setupConnection() {
      if (chrome?.runtime) {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const connection = chrome.tabs.connect(tab.id, { name: portName });
        connection.onMessage.addListener(chromeMessageListener);
        port.current = connection;
      }
    }

    setupConnection();
  }, [handleDocumentTextRetrieved])

  useEffect(() => {
    if (port?.current && searchResults?.length > 0) {
      port.current.postMessage({
        action: FIND_PASSAGES,
        payload: searchResults
      });
    }
  }, [searchResults]);


  const handleClickResult = (result) => {
    setSelectedPassageRank(result.rank);
    port?.current?.postMessage({
      action: SELECT_RESULT,
      payload: result,
    })
  }

  const handleSearch = async (query) => {
    setSearchQuery(query);
    setIsLoading(true);
    foundPassages.current = [];

    port?.current?.postMessage({ action: CLEAR_HIGHLIGHTS });
    port?.current?.postMessage({ action: REQUEST_PAGE, payload: { query }});
  }

  return (
    <div className="mx-auto w-96 shadow-lg rounded-sm px-4 py-8">
      <h1 className="text-2xl font-bold tracking-wide mb-8">Deep Finder</h1>

      <SearchForm
        handleSearch={handleSearch}
        isLoading={isLoading}
      />

      {visibleSearchResults && visibleSearchResults.length > 0 && (
        <ResultsList
          handleClickResult={handleClickResult}
          searchResults={visibleSearchResults}
          selectedPassageRank={selectedPassageRank}
        />
      )}
    </div>
  );
}

export default DeepFinder;
