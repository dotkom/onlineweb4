var RS_DEBUG = 1;
var resources = ['notifier', 'mailinglists', 'infopages', 'gameservers', 'github', 'irc'];

function rslog(msg) {
	if (RS_DEBUG) {
		console.log('ResourceCenter:', msg);
	}
}

// Wait till the document is ready
$(function() {

	var toggleDetails = function() {
		var speed = 250;

		// Is facade showing?
		if ($(this).find('.facade').css('top') == '0px') {

			var thisId = $(this).attr('id');
			rslog('Show details for ' + thisId);
			
			// Slide the facade up
			$(this).find('.facade').animate({
				top:'-200pt',
				opacity:'0',
			}, speed, function() {
				$(this).find('.facade').css('z-index','-100');
			});
			$(this).find('.details').animate({
				top:'-207pt',
				opacity:'1',
			}, speed, function() {
				$(this).find('.facade').css('z-index','100');
			});

			// Hide details for other resources
			for (var i = resources.length - 1; i >= 0; i--) {
				var elementId = '#' + resources[i];
				if (elementId != thisId) {
					var isFacade = $(elementId).find('.facade').css('top') == '0px';
					if (!isFacade) {
						rslog('Hiding ' + elementId);

						// Slide the facade up
						$(elementId).find('.facade').animate({
							top:'0pt',
							opacity:'1',
							'z-index':'100',
						}, speed, function() {
							$(elementId).find('.facade').css('z-index','100');
						});
						$(elementId).find('.details').animate({
							top:'0pt',
							opacity:'0',
						}, speed, function() {
							$(elementId).find('.facade').css('z-index','-100');
						});
					}
				}
			};
		}
	};

	// Bind click function for all resources
	for (var i = resources.length - 1; i >= 0; i--) {
		var elementId = '#' + resources[i];
		$(elementId).click(toggleDetails);
	};

	$('.flipbox').click(function(){

		$(".flipbox").flippy({
		    color_target: "red",
		    duration: "500",
		    verso: "woo<b>hoo</b>"
		 });
		$('.flipbox').unbind('click').click(function(){
			$(".flipbox").flippyReverse();
		});

	});

});