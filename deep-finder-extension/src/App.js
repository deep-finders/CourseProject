/* eslint-disable no-undef */
import React, { useState, useEffect } from 'react';
import './App.css';
import ResultsList from './components/ResultsList';
import SearchForm from './components/SearchForm';
import { search } from './services/searchService';

function App() {

  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const handleDocumentTextRetrieved = async (documentText) => {

    const results = await search(searchQuery, documentText)
    console.log('(handleDocumentTextRetrieved) results:', results)

    setIsLoading(false);
    setSearchResults(results);
  }

  useEffect(() => {
    console.log('App.js useEffect')

    const chromeMessageListener = (request, sender, sendResponse) => {
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
        console.log('')
        chrome.runtime.onMessage.removeListener(chromeMessageListener)
      }
    }
  }, [])

  const handleClickResult = (result) => {
    if (chrome && chrome.runtime) {
      chrome.runtime.sendMessage({
        result
      })
    }
  }

  const handleSearch = async (searchQuery) => {
    setIsLoading(true);

    if (chrome && chrome.tabs) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          chrome.runtime.sendMessage({
            documentHtml: document.body.innerHTML,
            documentText: document.body.innerText,
            documentPTags: document.querySelectorAll("p"),
          }, function (response) {
            console.info('(executeScript) response:', response);
          })

          chrome.runtime.onMessage.addListener((request, sender) => {
            console.log('(webpage) request:', request);
            console.log('(webpage) sender:', sender);
          })
        }
      })
    } else {
      handleDocumentTextRetrieved(searchQuery, '');
    }
  }

  return (
    <main className="mx-auto w-96 shadow-lg rounded-sm px-4 py-8">
      <h1 className="text-2xl font-bold tracking-wide mb-8">Deep Finder</h1>

      <SearchForm
        handleSearch={handleSearch}
        isLoading={isLoading}
        searchQuery={searchQuery}
        updateSearchQuery={setSearchQuery}
      />

      {searchResults && searchResults.length > 0 && (
        <ResultsList
          handleClickResult={handleClickResult}
          searchResults={searchResults}
        />
      )}

    </main>
  );
}

export default App;
