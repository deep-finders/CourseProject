import React, { useState } from 'react';

import { ReactComponent as SearchIcon } from '../icons/search-icon.svg';

const SearchForm = ({
	handleSearch = () => {},
	isLoading = false,
}) => {

	const [searchQuery, setSearchQuery] = useState('');

	const handleSubmit = (e) => {
		e.preventDefault();
		handleSearch(searchQuery);
	}

	return (
		<form onSubmit={handleSubmit} className="space-y-4">
			<div className="">
				<label htmlFor="query-input" className="block text-sm font-medium text-gray-700">Search</label>
				<input
					name="query-input"
					id="query-input"
					className="bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal"
					value={searchQuery}
					onChange={({ target }) => setSearchQuery(target.value)}
				/>
			</div>
			<button
				className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 flex flex-nowrap items-center justify-center space-x-2"
				type="submit"
				disabled={isLoading}
			>
				<SearchIcon className="h-5 w-5 fill-current"/>
				<span>Search</span>
			</button>
		</form>
	)
}

export default SearchForm;
