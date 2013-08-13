$(document).ready(function() {
    $('#image-name').hide();
});

$('input[type=file]').change(function() {
    var filename = $('input[type=file]').val().split('\\').pop();
    $('#image-name').val(filename);
    $('#image-name').show();
});

//$(".fadeload").bind("load", function () { $(this).fadeIn('slow'); });

//$(function() {
//    $("#profile-image").hover(function() {
//        $(this).animate({
//            opacity: 0.2
//        });
//    }, function() {
//        $(this).stop(true, true).animate({
//            opacity: 1
//        });
//    });
//});