var RS_DEBUG = 1;
var resources = ['notifier', 'mailinglists', 'infopages', 'gameservers', 'github', 'irc'];

function rslog(msg) {
	if (RS_DEBUG) {
		console.log('ResourceCenter:', msg);
	}
}

// Wait till the document is ready
$(function() {
	// nothing here yet
});
