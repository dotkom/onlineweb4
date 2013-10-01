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
    // var card_width = $('.flipper').outerWidth();
    // // Container
    // $('.flipper').css({'height':card_width+'px'});
    // // Front and back
    // $('.flip-container').css({'height':card_width+'px'});
    // $('.front').css({'height':(card_width-2)+'px'});
    // $('.back').css({'height':(card_width-4)+'px'});
    // // // Image
    // $('.front img').css({'height':(card_width-4)+'px', 'width':(card_width)+'px'});
    // // Fonts
    // if (card_width <= 260) {
    //     $('.back h3').attr('style', 'font-size: 11pt; margin-top:-3pt; margin-bottom:-3pt;');
    //     $('.back p').attr('style', 'font-size: 9pt; line-height:12pt;');
    //     $('.back ul').attr('style', 'font-size: 9pt;');
    //     $('.back li').attr('style', 'margin-top:-3pt; margin-bottom:-3pt;');
    // }
    // else {
    //     $('.back h3').attr('style', '');
    //     $('.back p').attr('style', '');
    //     $('.back ul').attr('style', '');
    //     $('.back li').attr('style', '');
    // }
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
