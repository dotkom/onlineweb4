$(document).ready(function () {
    $('div.tagcloud span').each(function () {
        frequency = $(this).data('frequency');
        rel = (frequency / 10 < 1) ? frequency / 10 + 1: (frequency / 10 > 2) ? "2" : frequency / 10;
        $(this).css("font-size", rel + 'em');
        if(rel < 1.2) {
            rel = 400;
        } else if(rel < 1.5) {
            rel = 600;
        } else if(rel < 1.7) {
            rel = 700;
        } else {
            rel = 800;
        }
        $(this).css("font-weight", rel);
    });
});
