/* eslint-disable no-undef */
import React, { useCallback, useState, useEffect } from 'react';

import './App.css';
import ResultsList from './components/ResultsList';
import SearchForm from './components/SearchForm';
import { search } from './services/searchService';


const SELECT_RESULT = 'select_result';
const REQUEST_PAGE = 'request_page';
const SEND_PAGE = 'send_page';

const DeepFinder = () => {

  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPassageRank, setSelectedPassageRank] = useState();
  const [port, setPort] = useState();

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
      setIsLoading(false);
      setSearchResults(results);

    } catch(e) {
      console.error(e);
      setIsLoading(false);
    }
  }, [])

  useEffect(() => {
    const chromeMessageListener = ({ action, payload}) => {
      console.info('Handing message:', { action, payload });

      if (action === SEND_PAGE) {
        handleDocumentTextRetrieved({ ...payload })
      }
    }

    async function setupConnection() {
      if (chrome && chrome.runtime) {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const connection = chrome.tabs.connect(tab.id, { name: 'deep-finder' });
        connection.onMessage.addListener(chromeMessageListener);
        setPort(connection);
      }
    }

    setupConnection();

    return () => {
      port && port.disconnect();
    }
  }, [handleDocumentTextRetrieved])

  const handleClickResult = (result) => {
    setSelectedPassageRank(result.rank);
    port && port.postMessage({
      action: SELECT_RESULT,
      payload: result,
    })
  }

  const handleSearch = async (query) => {
    setSearchQuery(query);
    setIsLoading(true);

    port.postMessage({ action: REQUEST_PAGE, payload: { query }});
  }

  return (
    <div className="mx-auto w-96 shadow-lg rounded-sm px-4 py-8">
      <h1 className="text-2xl font-bold tracking-wide mb-8">Deep Finder</h1>

      <SearchForm
        handleSearch={handleSearch}
        isLoading={isLoading}
      />

      {searchResults && searchResults.length > 0 && (
        <ResultsList
          handleClickResult={handleClickResult}
          searchResults={searchResults}
          selectedPassageRank={selectedPassageRank}
        />
      )}
    </div>
  );
}

export default DeepFinder;
