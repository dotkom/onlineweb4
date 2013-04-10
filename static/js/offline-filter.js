function init_offline() {
    var num = Math.floor($('#offline-wrapper').width()/167);
    var rows = Math.ceil(numIssuesToDisplay/num);
    $('#offline-wrapper').stop().animate({height: (rows*226)},400);
}

var numIssuesToDisplay = 8;
var busy = false;

$(function() {
    $('.filter-year').on('click', function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        if (!busy) {
            busy = true;
            
            // Swap classes
            $("#filter-menu .active").removeClass("active");
            $(this).parent().addClass("active");
            
            // The sort
            filter($(this).html());
        }
    });
    
    $('#filter-reset').on('click', function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        if (!busy) {
            busy = true;
            if ($('#filter-menu .active').length > 0){
                $('#filter-menu .active').removeClass('active');
                $('.offline_issue:visible').fadeOut(400,function () {
                    if ($(".offline_issue:animated").length === 0) {
                        $('.offline_issue').fadeIn(400,function () {
                            if ($(".offline_issue:animated").length === 0)
                                busy = false;
                        });
                    }
                });
            }
        }
    });
    
    init_offline();
    
    $(window).on('resize',init_offline);
});

function filter(year) {
    $('.offline_issue:visible').stop().fadeOut(350);
    $('.offline_issue').each(function () {
        if (parseInt(year) == parseInt($(this).data('year'))) {
            $(this).delay(400).fadeIn(400,function () {
                if ($('.offline_issue:animated').length === 0) {
                    busy = false;
                }
            });
        }
    });
}