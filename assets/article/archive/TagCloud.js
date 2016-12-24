
$(document).ready(function () {
    $('div.tagcloud span').each(function () {
        var max = $('div.tagcloud').data('max_frequency');
        console.log(max);
        frequency = $(this).data('frequency');
        rel = ((frequency / (max/3)) + 1);
        $(this).css("font-size", rel + 'em');
        if(rel < 2) {
            rel = 400;
        } else if(rel < 2.5) {
            rel = 600;
        } else if(rel < 3.5) {
            rel = 700;
        } else {
            rel = 800;
        }
        $(this).css("font-weight", rel);
    });
});
