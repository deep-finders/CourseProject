/**
 * Constants
 */
const SELECT_RESULT = 'select_result';
const REQUEST_PAGE = 'request_page';
const SEND_PAGE = 'send_page';

//AI: remove or update markJsDefaultConfig
const markJsDefaultConfig = {
	acrossElements: true,
	className: 'highlight',
	debug: true,
	element: 'span',
	ignoreJoiners: false,
	separateWordSearch: 'false',
}

/**
 *
 * @param {object} result Passage result
 * @param {number} result.id
 * @param {string} result.passage
 */
function handleHighlightPassage(result) {
	console.log('selected result:', result);
	markDocument(result.passage);
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
	//Removes previous marks
	markJs.unmark({ done: function(){
		//Adds new marks
		markJs.mark(passage, {
			"separateWordSearch": false,
			"debug": true,
			"acrossElements": true,
			"className": "highlight",
			//"accuracy": {
			//	"value": "exactly",
			//	"limiters": [",", ".","'","\""]
			//},
			done: function () {
				//AI: Add code to handle exceptions when no match
				var elements = document.getElementsByClassName("highlight");
				var markedElemend = elements[0];
				markedElemend.scrollIntoView({
					behavior: 'auto',
					block: 'center',
					inline: 'center'
				});
			}
		})
	}})
}

if (chrome && chrome.runtime) {
	chrome.runtime.onConnect.addListener(port => {
		console.log('Connected to port:', port);
	
		if (port.name === 'deep-finder') {
			port.onMessage.addListener(handleOnMessage);
		}
	});
}
