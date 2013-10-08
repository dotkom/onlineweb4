var RS_DEBUG = 0;

function rslog(msg) {
	if (RS_DEBUG) {
		console.log('Resourcecenter:', msg);
	}
}

function resize() {
    var width = $('.flip-container:first').width();
    $('.flip-container').attr('style', 'height:'+width+'px;');
    $('.front').attr('style', 'height:'+width+'px;');
    $('.back').attr('style', 'height:'+width+'px;');
}

function onClick() {
    var flip = '-webkit-transform:rotateY(180deg);-moz-transform:rotateY(180deg);transform:rotateY(180deg);-ms-filter:"FlipH";filter:FlipH;';
    
    // check if already applied
    var flipper = $(this).find('.flipper');
    var style = $(flipper).attr('style');
    
    if (style != flip) {
        // flip it
        $(this).find('.flipper').attr('style', flip);
        // flip all others back
        $('.flip-container').not(this).find('.flipper').attr('style', '');
    }
    else {
        $(flipper).attr('style',''); // backflip, lol
    }
}

// Wait till the document is ready
$(function() {
	// Resize cards
	resize();
	// Bind card resizing to window resize as well
	$(window).resize(resize);
    // Bind cards to click function
    $('.flip-container').click(onClick);
});
