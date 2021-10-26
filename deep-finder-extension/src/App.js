/* eslint-disable no-undef */
import React, { useState } from 'react';
import './App.css';
import ResultsList from './components/ResultsList';
import SearchForm from './components/SearchForm';

function App() {

  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  const handleDocumentTextRetrieved = (documentText) => {
    console.log('documentText:', documentText);

    setIsLoading(false);
    setSearchResults([]);
  }

  const handleSearch = async (searchQuery) => {
    setIsLoading(true);

    if (chrome) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      console.info('tab:', tab);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          handleDocumentTextRetrieved(document.body.innerText);
        }
      })
    }
  }

  return (
    <main className="mx-auto w-96 shadow-lg rounded-sm px-4 py-8">
      <h1 className="text-2xl font-bold tracking-wide mb-8">Deep Finder</h1>

      <SearchForm
        handleSearch={handleSearch}
        isLoading={isLoading}
      />

      { searchResults && searchResults.length > 0 && (
        <ResultsList searchResults={searchResults} />
      )}

    </main>
  );
}

export default App;
