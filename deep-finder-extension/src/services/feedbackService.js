const API_ROOT = 'https://deepfindersfa.azurewebsites.net/api/HttpDeepFindProvideFeedbackTrigger?code=xjx9fLuR3bJdVKs6ExXnRt2jcV3CUbfogHsU3rWnJzfOgvBaydW73Q==';

const submitFeedback = async ({
	id,
	feedback,
}) => {
	const response = await fetch(`${API_ROOT}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			result_id: id,
			feedback,
		})
	});
	return response.json();
}

export { submitFeedback };
