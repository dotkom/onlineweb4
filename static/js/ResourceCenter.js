var RS_DEBUG = 1;

function rslog(msg) {
	if (RS_DEBUG) {
		console.log('ResourceCenter:', msg);
	}
}

// Wait till the document is ready
$(function() {

	var toggleDetails = function() {
		var speed = 250;
		var isToggled = $(this).find('.facade').css('top') == '0px';
		if (isToggled) {
			rslog('Show details for', $(this.id));
			// Slide the facade up
			$(this).find('.facade').animate({
				top:'-200pt',
				opacity:'0',
			}, speed);
			$(this).find('.details').animate({
				top:'-200pt',
				opacity:'1',
			}, speed);
		}
		else {
			rslog('Show facade', $(this.id));
			// Slide the facade down
			$(this).find('.facade').animate({
				top:'0pt',
				opacity:'1',
			}, speed);
			$(this).find('.details').animate({
				top:'0pt',
				opacity:'0',
			}, speed);
		}
	};

	$('#notifier').click(toggleDetails);

});