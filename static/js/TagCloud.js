$(document).ready(function () {
    $('div.tagcloud span').each(function () {
        frequency = $(this).data('frequency');
        $(this).css("fontSize", (frequency / 10 < 1) ? frequency / 10 + 1 + "em": (frequency / 10 > 2) ? "2em" : frequency / 10 + "em");
    });
});
