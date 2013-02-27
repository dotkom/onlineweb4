$(function() {
    $('.filter-year').on('click', function(e) {
        e.preventDefault();
        $("#filter-menu .active").removeClass("active")
        $(this).parent().addClass("active")
        filter($(this).html());
    });
    
    $('#filter-reset').on('click', function(e) {
        e.preventDefault();
        if ($('#filter-menu .active').length > 0){
            $('#filter-menu .active').removeClass('active');
            
            $.each($('.offline_issue'), function () {
                if ($(this).parent().is(':hidden')) {
                    $(this).parent().fadeIn(400);
                }
            });
        }
    });
});

function filter(year) {
    var fadeIns = new Array();
    var timeout = 0;
    $.each($('.offline_issue'), function(index, item) {
        if(parseInt(year) != parseInt($(this).data('year'))) {
            if($(this).parent().is(':visible')) {
                $(this).parent().fadeOut(400);
                timeout += 400;
            }
        }
        else {
            if ($(this).parent().is(':hidden')) {
                fadeIns.push(this.id);
            }
        }
    });
        setTimeout(function () {
            for (i = 0; i < fadeIns.length; i++) {
                $('#'+fadeIns[i]).parent().fadeIn(400);}
            },timeout+50);
}
