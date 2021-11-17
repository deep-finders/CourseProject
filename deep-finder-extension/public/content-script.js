/**
 * Constants
 */
const SELECT_RESULT = 'select_result';
const REQUEST_PAGE = 'request_page';
const SEND_PAGE = 'send_page';

const markJsDefaultConfig = {
	element: 'span',
	className: 'highlight',
}

/**
 * 
 * @param {object} result Passage result
 * @param {number} result.id
 * @param {string} result.passage
 */
function handleHighlightPassage(result) {
	console.log('selected result:', result);
}

function handleOnMessage({ action, payload }, port) {
	console.info('Handing message:', { action, payload });
	switch (action) {
		case SELECT_RESULT: {
			handleHighlightPassage(payload);
			break;
		}

		case REQUEST_PAGE: {
			port && port.postMessage({
				action: SEND_PAGE,
				payload: {
					documentHtml: document.body.innerHTML,
					documentText: document.body.innerText,
					documentPTags: Array.from(document.querySelectorAll('p')).map(p => p.innerHTML),
					pageUrl: window.location.href,
					query: payload.query,
				}
			})
			break;
		}

		default:
			return;
	}
}

function markDocument(passage) {
	const markJs = new Mark(document.querySelector("body"));
	markJs.mark(passage)
}

if (chrome && chrome.runtime) {
	chrome.runtime.onConnect.addListener(port => {
		console.log('Connected to port:', port);
	
		if (port.name === 'deep-finder') {
			port.onMessage.addListener(handleOnMessage);
		}
	});
}
