/* eslint-disable no-undef */
import React, { useState } from 'react';
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

    setIsLoading(false);
    setSearchResults(results);
  }

  const handleSearch = async (searchQuery) => {
    setIsLoading(true);

    if (chrome && chrome.tabs) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      console.info('tab:', tab);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          handleDocumentTextRetrieved(searchQuery, document.body.innerText);
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

      { searchResults && searchResults.length > 0 && (
        <ResultsList searchResults={searchResults} />
      )}

    </main>
  );
}

export default App;
