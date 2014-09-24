var ML_DEBUG = 0;

function mllog(msg) {
	if (ML_DEBUG) {
		console.log('Mailinglists:', msg);
	}
}

// Wait till the document is ready
$(function() {
	// Masonry
    var container = document.querySelector('#masonry');
    var masonry = new Masonry( container, {
      // options
      gutter: 10,
      columnWidth: 260,
      itemSelector: '.mailinglist',
    });
    setTimeout(function() {
    	// If Masonry didn't get it right the first time
    	masonry.layout();
    }, 1500);

   $('.members .title').on('click', function () {
    $(this).find('.glyphicon').toggleClass('glyphicon-chevron-up').toggleClass('glyphicon-chevron-down');
   }); 
});
