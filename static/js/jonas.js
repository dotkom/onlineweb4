$(document).ready(function() {
    function scrolltothis(from, to) {
        $(from).click(function() {
            var topPosition = jQuery(to).offset().top - 57; //See margin-top on body element
            jQuery('html, body').animate({scrollTop:topPosition}, 'slow');
        });
    }
    scrolltothis('#home', 'body');
    scrolltothis('#arrangementer', '#arrangementer-heading');
    scrolltothis('#artikler', '#artikler-heading');
});
