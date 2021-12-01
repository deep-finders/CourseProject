/**
 * Constants
 */
const portName = 'deep-finder';

// Content Script Actions
const SEND_PAGE = 'send_page';
const PASSAGE_FOUND = 'passage_found';

// Extension Actions
const CLEAR_HIGHLIGHTS = 'clear_highlights';
const FIND_PASSAGES = 'find_passages';
const REQUEST_PAGE = 'request_page';
const SELECT_RESULT = 'select_result';

const markJsDefaultConfig = {
	acrossElements: true,
	className: 'highlight',
	debug: true,
	element: 'span',
	iframes: true,
	ignoreJoiners: false,
	separateWordSearch: false,
}

/**
 *
 * @param {object} result - passage result
 * @param {number} result.id
 * @param {string} result.passage
 */
function handleHighlightPassage(result) {
	markDocument(result);
}

/**
 * 
 * @param {event}
 * @param {string} event.action
 * @param {object} event.payload
 * @param {object} port - reuse long-lived connection
 * @returns
 */
function handleOnMessage({ action, payload }, port) {
	console.info('Handing message:', { action, payload });
	switch (action) {
		case CLEAR_HIGHLIGHTS: {
			unmarkHighlights();
			break;
		}

		case FIND_PASSAGES: {
			payload.forEach((foundResult, i) => {
				findPassage(foundResult, port);
			});
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

		case SELECT_RESULT: {
			unmarkHighlights(() => {
				handleHighlightPassage(payload);
			});
			break;
		}

		case PASSAGE_FOUND: {
			console.log('(content-script) passage found:', payload);
			break;
		}

		default:
			return;
	}
}

/**
 * Unmarks all MarkJS highlights
 * @param {function} doneCallback
 */
function unmarkHighlights(doneCallback = () => {}) {
	const markJs = new Mark(document.querySelector('body'));
	markJs.unmark({
		className: 'highlight',
		done: () => { doneCallback() }
	});
}

function findPassage(result, port) {
	const markJs = new Mark(document.querySelector('body'));
	markJs.mark(result.passage, {
		...markJsDefaultConfig,
		className: '',
		done: (numMarks) => {
			if (port && numMarks) {
				port.postMessage({
					action: PASSAGE_FOUND,
					payload: result
				})
			}
		}
	})
}

function markDocument(result) {
	const markJs = new Mark(document.querySelector('body'));
	markJs.mark(result.passage, {
		...markJsDefaultConfig,
		className: 'highlight',
		each: (element) => {
			element && element.scrollIntoView({
				behavior: 'smooth',
				block: 'center',
			});
		}
	})
}


try {
	unmarkHighlights();
} catch(e) {
	console.error('Error unmarking highlights on load:', e);
}

if (chrome && chrome.runtime) {
	chrome.runtime.onConnect.addListener(port => {
		console.log('Connected to port:', port);

		if (port.name === portName) {
			port.onMessage.addListener(handleOnMessage);
		}
	});
}
