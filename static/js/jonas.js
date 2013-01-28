$(document).ready(function() {

    function scrolltothis(from, to) {

        $(from).click(function() {
            var topPosition = jQuery(to).offset().top - 57; // See body margin
            jQuery('html, body').animate({scrollTop:topPosition}, 'slow');
        });

    }

    scrolltothis('#events', '#events-heading');
    scrolltothis('#articles', '#articles-heading');
    scrolltothis('#about', '#about-heading');
    scrolltothis('#business', '#business-heading');
    scrolltothis('#offline', '#offline-heading');

});
