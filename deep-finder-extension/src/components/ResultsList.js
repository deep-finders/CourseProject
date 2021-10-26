import React from 'react';
import SearchResult from './SearchResult';

const ResultsList = ({
	searchResults = [],
}) => {

	return (
		<section>
			{searchResults.map((searchResult, index) => (
				<SearchResult searchResult={searchResult} key={`search-result-${index}`} />
			))}
		</section>
	)
}

export default ResultsList;
