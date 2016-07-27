
var _addNotifier = 'Add Notifier to Chrome';
var _failedToAddNotifier = 'Adding Failed :(';
var _addedNotifier = 'Added to Chrome <3';

function _installNotifier() {
	chrome.webstore.install('https://chrome.google.com/webstore/detail/hfgffimlnajpbenfpaofmmffcdmgkllf',
	function() {
		$('#install_notifier').text(_addedNotifier)
		setTimeout(function() {
			$('#install_notifier').fadeOut('slow');
		}, 8000);
	}, function() {
		$('#install_notifier').text(_failedToAddNotifier)
		setTimeout(function() {
			$('#install_notifier').text(_addNotifier)
		}, 3000);
	});
}

$(function(){

	var _isChrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
	var _isNotifierInstalled = chrome.app.isInstalled;

	if (_isChrome && !_isNotifierInstalled) {
		$('body').append('<button class="install-notifier" id="install_notifier" onclick="_installNotifier();">'
			+ _addNotifier + '</button>');
	}
});