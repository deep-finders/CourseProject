/* eslint-disable no-undef */
import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import ResultsList from './components/ResultsList';
import SearchForm from './components/SearchForm';
import { search } from './services/searchService';

const DeepFinder = () => {

  const [isLoading, setIsLoading] = useState(false);
  // const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const inputRef = useRef();

  const handleDocumentTextRetrieved = async ({
    documentHtml,
    documentText,
    documentPTags,
    pageUrl,
  }) => {
    try {
      const results = await search({
        documentHtml,
        documentText,
        documentPTags,
        pageUrl,
        query: inputRef.current.value,
      })
      console.log('(handleDocumentTextRetrieved) results:', results)

      setIsLoading(false);
      setSearchResults(results);

    } catch(e) {
      console.error(e);
      setIsLoading(false);
    }
  }

  useEffect(() => {
    const chromeMessageListener = (request, sender) => {
      console.info('request:', request);
      console.info('sender:', sender);
      const { documentHtml, documentText, documentPTags } = request;

      handleDocumentTextRetrieved({
        documentHtml,
        documentText,
        documentPTags,
        pageUrl: sender.url,
      })
    }

    if (chrome && chrome.runtime) {
      chrome.runtime.onMessage.addListener(chromeMessageListener)
    }

    return () => {
      if (chrome && chrome.runtime) {
        console.log('Removing chrome runtime listener')
        chrome.runtime.onMessage.removeListener(chromeMessageListener)
      }
    }
  }, [])

  const handleClickResult = (result) => {
    console.log('clicked result:', result);
    if (chrome && chrome.runtime) {
      chrome.runtime.sendMessage({
        result
      })
    }
  }

  const handleSearch = async () => {
    setIsLoading(true);

    if (chrome && chrome.tabs) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          chrome.runtime.sendMessage({
            documentHtml: document.body.innerHTML,
            documentText: document.body.innerText,
            documentPTags: Array.from(document.querySelectorAll("p")).map(p => p.innerHTML),
          });

          chrome.runtime.onMessage.addListener((request, sender) => {
            console.log('(webpage) request:', request);
            console.log('(webpage) sender:', sender);
          })
        }
      })
    } else {
      handleDocumentTextRetrieved({
        documentHtml: document.body.innerHTML,
        documentText: document.body.innerText,
        documentPTags: document.querySelectorAll("p"),
      }, '');
    }
  }

  // const handleUpdateSearchQuery = (e) => {
  //   console.log('(handleUpdateSearchQuery) searchQuery:', searchQuery);
  //   console.log('e.target.value:', e.target.value);
  //   setSearchQuery(e.target.value)
  // }

  return (
    <div className="mx-auto w-96 shadow-lg rounded-sm px-4 py-8">
      <h1 className="text-2xl font-bold tracking-wide mb-8">Deep Finder</h1>

      <SearchForm
        handleSearch={handleSearch}
        isLoading={isLoading}
        // searchQuery={searchQuery}
        // updateSearchQuery={handleUpdateSearchQuery}
        ref={inputRef}
      />

      {searchResults && searchResults.length > 0 && (
        <ResultsList
          handleClickResult={handleClickResult}
          searchResults={searchResults}
        />
      )}
    </div>
  );
}

export default DeepFinder;
