import React from 'react';
import SearchResult from './SearchResult';

const ResultsList = ({
	handleClickResult = () => {},
	searchResults = [],
}) => {

	return (
		<>
			<div className="flex my-4 space-x-4 items-center">
				<div className="h-1 border-t border-gray-200 border-solid w-full"></div>
				<span className="flex-grow whitespace-nowrap">{`${searchResults.length} results found`}</span>
				<div className="h-1 border-t border-gray-200 border-solid w-full"></div>
			</div>

			<section className="flex flex-col space-y-4 max-h-96 overflow-y-scroll">
				{searchResults.map((searchResult, index) => (
					<SearchResult
						handleClickResult={handleClickResult}
						searchResult={searchResult} key={`search-result-${index}`}
					/>
				))}
			</section>
		</>
	)
}

export default ResultsList;
