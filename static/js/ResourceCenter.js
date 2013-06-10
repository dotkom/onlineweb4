
$(function() {
	var showDetails = function() {
		alert('yep')
		$(this).find('.facade').animate({
			top:'-200pt',
		}, 200);
		$(this).find('.details').animate({
			top:'0pt',
		}, 200);
	};
	$('#notifier').click(showDetails);
});