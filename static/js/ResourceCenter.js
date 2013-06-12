// Wait till the document is ready
$(function() {

	var toggleDetails = function() {
		var isToggled = $(this).find('.facade').css('top') == '0px';
		if (isToggled) {
			// Slide the facade up
			$(this).find('.facade').animate({
				top:'-200pt',
			}, 150);
			$(this).find('.details').animate({
				top:'-200pt',
			}, 150);
		}
		else {
			// Slide the facade down
			$(this).find('.facade').animate({
				top:'0pt',
			}, 150);
			$(this).find('.details').animate({
				top:'0pt',
			}, 150);
		}
	};

	$('#notifier').click(toggleDetails);

});