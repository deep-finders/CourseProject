const API_ROOT = 'https://deepfindersfa.azurewebsites.net/api/HttpDeepFindTrigger?code=6bDwaxTAGKSjKk9kCfx2b0SeoT0GrBUS7aClM9Yjz8pYzoGbHLGukg=='

const search = async ({
	documentHtml,
	query,
}) => {
	const response = await fetch(`${API_ROOT}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			documentHtml,
			query,
		})
	});
	return response.json();
}

export { search };
