const API_ROOT = 'https://placeholder.io/something'
const MOCK_API_ROOT = 'http://localhost:3004';

const search = async (query, text) => {

	if (process.env.NODE_ENV !== 'production') {
		return getMockData();
	};

	const response = await fetch(`${API_ROOT}/searchResults`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ query, text })
	});

	return response.json();
}

const getMockData = async () => {

	const response = await fetch(`${MOCK_API_ROOT}/searchResults`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
	});

	return response.json();
}

export { search };
