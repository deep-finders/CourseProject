const TEXT_TO_SEARCH = "test"

console.log("Running content script 2")
//src = "node_modules/mark.js/dist/mark.min.js"
var instance = new Mark(document.querySelectorAll("body"));
instance.mark(TEXT_TO_SEARCH, {
    "accuracy": "exactly",
    "acrossElements": true,
    "separateWordSearch": false
});