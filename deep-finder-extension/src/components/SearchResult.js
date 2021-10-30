import React from 'react';

const SearchResult = ({
	onClickResult,
	searchResult,
}) => {
	const { id, passage } = searchResult;

	return (
		<div
			className="px-2 py-3 hover:shadow-md transition-all rounded-md shadow-sm border-gray-300 border border-solid cursor-pointer hover:bg-gray-50"
			onClick={() => onClickResult(searchResult)}
		>
			<p className="truncate">{passage}</p>
		</div>
	)
}

export default SearchResult;
