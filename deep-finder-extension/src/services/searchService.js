const API_ROOT = 'https://deepfindersfa.azurewebsites.net/api/HttpDeepFindTrigger?code=6bDwaxTAGKSjKk9kCfx2b0SeoT0GrBUS7aClM9Yjz8pYzoGbHLGukg=='
const MOCK_API_ROOT = 'http://localhost:3004';

const search = async (query, text) => {

	if (process.env.NODE_ENV !== 'production') {
		return getMockData();
	};

	const response = await fetch(`${API_ROOT}`, {
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
