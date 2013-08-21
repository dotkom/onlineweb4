var RS_DEBUG = 1;

function rslog(msg) {
	if (RS_DEBUG) {
		console.log('Resourcecenter:', msg);
	}
}

function resize() {
    var card_width = $('.flipper').outerWidth();
    // Container
    $('.flipper').css({'height':card_width+'px'});
    // Front and back
    $('.front').css({'height':card_width+'px'});
    $('.back').css({'height':card_width+'px'});
    // // Image
    // $('.front img').css({'height':card_width+'px'});
}

// Wait till the document is ready
$(function() {
	// Resize cards
	resize();
	// Bind it to window resize as well
	$(window).resize(resize);
});
