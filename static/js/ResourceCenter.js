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
		var isFacade = $(this).find('.facade').css('top') == '0px';
		if (isFacade) {
			var id = $(this).attr('id');
			rslog('Show details for ' + id);
			// Slide the facade up
			$(this).find('.facade').animate({
				top:'-200pt',
				opacity:'0',
			}, speed, function() {
				$('#'+id).find('.facade').css('z-index','-1000');
			});
			$(this).find('.details').animate({
				top:'-207pt',
				opacity:'1',
			}, speed);
		}
		// else {
		// 	rslog('Show facade ' + $(this).attr('id'));
		// 	// Slide the facade down
		// 	$(this).find('.facade').animate({
		// 		top:'0pt',
		// 		opacity:'1',
		// 	}, speed);
		// 	$(this).find('.details').animate({
		// 		top:'0pt',
		// 		opacity:'0',
		// 	}, speed);
		// }
	};

	$('#notifier').click(toggleDetails);
	$('#mailinglists').click(toggleDetails);
	$('#infopages').click(toggleDetails);
	$('#gameservers').click(toggleDetails);
	$('#github').click(toggleDetails);
	$('#irc').click(toggleDetails);

});