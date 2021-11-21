console.info('Content script loaded');

if (chrome && chrome.runtime) {
	console.log('chrome runtime found');

		chrome.runtime.onMessage.addListener((request, sender) => {
			console.log('(webpage) request:', request);
			console.log('(webpage) sender:', sender);
		});
}
