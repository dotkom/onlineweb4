
$(function() {
	var maximize = function() {
		$(this).find('img').animate({
			width:'100%',
			height:'100%',
		}, 200);
	};
	$('#github').click(maximize);
});