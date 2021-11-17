import React from 'react';

const SearchResult = ({
	handleClickResult,
	isSelected = false,
	searchResult,
}) => {
	const { id, passage, rank } = searchResult;

	return (
		<div
			className="px-2 py-3 hover:shadow-md transition-all rounded-md shadow-sm border-gray-300 border border-solid cursor-pointer hover:bg-gray-50"
			onClick={() => handleClickResult(searchResult)}
		>
			<p className="">{passage}</p>
		</div>
	)
}

export default SearchResult;
