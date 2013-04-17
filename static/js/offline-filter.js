var offline_num_in_row = 1; // Number of issues in a single row (may change on resize)
var offline_total_rows = 1; // Number of total rows (calculated based on the number of total issues to display)
var num_issues_to_display = 4; // Number of total issues
var num_issues_to_display_max = num_issues_to_display;
var offline_num_in_row_previous = 1337; // The previous number of total issues

$(function() {
    $('.filter-year').on('click', function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();

        // Swap classes
        $("#filter-menu .active").removeClass("active");
        $(this).parent().addClass("active");
            
        // The sort
        filter($(this).html());
    });
    
    $('#filter-reset').on('click', function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        num_issues_to_display = num_issues_to_display_max;
        
        $('.offline_issue').each(function() {
            $obj = $(this);
            if (!$obj.hasClass('displayable'))
                $obj.addClass('displayable');
        });
        
        init_offline(true);
        
    });
    
    
    $('#offline-nav').on('click','a',function(e) {
        console.log('hei');
        // Ztop def
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        // Variablez
        var $obj = $(this);
        
        // Doing stuff if nonmongo-user
        if (!$obj.parent().hasClass('disabled') && !$obj.parent().hasClass('acxtive')) {
            // Pre-selected index
            var selected_index = parseInt($('#offline-nav ul li.active a').attr('id').split('-')[1]);
            
            
            // Getting selected_indexxxx           
            if ($obj.hasClass('offline-nav')) {
                // The current nav-button is a indexed one
                var clicked_index = $obj.attr('id').split('-')[1];
            }
            else if (this.id == 'offline-nav-prev' || this.id == 'offline-nav-next') {
                // The current nav-button is previous/next
                if (this.id == 'offline-nav-prev')
                    clicked_index = selected_index - 1;
                else
                    clicked_index = selected_index + 1;
                     
            }
            else {
                // Håkej, so the current nav-button is first/last
                if (this.id == 'offline-nav-first')
                    clicked_index = 0;
                else
                    clicked_index = $('.offline-nav').length-1;
            }
            
            var num = 0;
            // Hide all the visible issues and fade in the new ones
            $('.offline_issue:visible').fadeOut(400,function () {
                if ($(".offline_issue:animated").length === 0) {

                    $('.offline_issue.displayable').each(function() {
                        if (num >= (num_issues_to_display*parseInt(clicked_index)) && num < (num_issues_to_display*(parseInt(clicked_index)+1))) {
                            $(this).fadeIn(400);
                        }
                        num++;
                    });
                }
            });
            
            // Removing active
            $('#offline-nav .active').removeClass('active');
            
            // Setting new active
            $('.offline-nav').eq(clicked_index).parent().addClass('active');
            
            // Active/unactive prev/next/last/first?
            var new_selected_index = $('#offline-nav ul li.active a').attr('id').split('-')[1];
            if (new_selected_index == 0) {
                $('#offline-nav-first').parent().addClass('disabled');
                $('#offline-nav-prev').parent().addClass('disabled');
                
                if ($('#offline-nav-next').parent().hasClass('disabled')) {
                    $('#offline-nav-next').parent().removeClass('disabled');
                    $('#offline-nav-last').parent().removeClass('disabled');
                }
            }
            else if (new_selected_index == ($('.offline-nav').length-1)) {
                $('#offline-nav-next').parent().addClass('disabled');
                $('#offline-nav-last').parent().addClass('disabled');
                
                if ($('#offline-nav-prev').parent().hasClass('disabled')) {
                    $('#offline-nav-prev').parent().removeClass('disabled');
                    $('#offline-nav-first').parent().removeClass('disabled');
                }
            }
        }
    });
    
    // Resize container 'n shit
    init_offline(false);
    
    // Fikser paginator
    init_pageinator();
    
    // On resize
    $(window).on("debouncedresize", init_offline(false));
});

function filter(year) {
    $('.offline_issue').each(function () {
        $obj = $(this);
        if (parseInt(year) == parseInt($obj.data('year'))) {
            if (!$obj.hasClass('displayable'))
                $obj.addClass('displayable');
        }
        else {
            if ($obj.hasClass('displayable'))
                $obj.removeClass('displayable');
        }
    });
    
    init_offline(true);
}

function init_offline(state) {
    // Checking to see if offline_rows_minimum is greater than the number of issues
    if ($('.offline_issue.displayable').length < num_issues_to_display)
        num_issues_to_display = $('.offline_issue.displayable').length;
    
    console.log(num_issues_to_display);
    // Number of issues in one row (this can change based on the width of the page)
    offline_num_in_row = parseInt(Math.floor($('#offline-wrapper').width()/182));
    console.log(offline_num_in_row);
    
    // Getting how many rows we have to display at once to display the minimum number of issues
    var offline_rows_minimum = parseInt(Math.ceil(num_issues_to_display/offline_num_in_row));
    console.log(offline_rows_minimum);
    
    // Animating the height of the container
    $('#offline-wrapper').css({height: (offline_rows_minimum*230)},400);
    
    // Storing total number of rows with issues
    offline_total_rows = parseInt(Math.ceil($('.offline_issue.displayable').length/(offline_num_in_row*offline_rows_minimum)));
    
    // Checking if we need to trigger a click and repaint the menu
    if (offline_num_in_row_previous == 1337)
        offline_num_in_row_previous = offline_total_rows;
    else {
        if (offline_num_in_row_previous != offline_total_rows || state) {
            offline_num_in_row_previous = offline_total_rows;
            init_pageinator();
        }
        else {
            offline_num_in_row_previous = offline_total_rows;
        }
        
    }
}

function init_pageinator() {
    // Removing first
    $('#offline-nav .pagination ul').empty();
    
    // Last/prev
    if (offline_total_rows > 1)
        $('#offline-nav .pagination ul').append('<li class="disabled"><a id="offline-nav-first" href="#">&#171;</a></li><li class="disabled"><a id="offline-nav-prev" href="#">&#8249;</a></li>');
    
    // Nums
    for (var i = 0; i < offline_total_rows; i++) {
        $('#offline-nav .pagination ul').append('<li'+((i == 0)?' class="active"':'')+'><a class="offline-nav" id="page-'+i+'" href="#">'+(i+1)+'</a></li>');
    }
    
    // Next/last
    if (offline_total_rows > 1)
        $('#offline-nav .pagination ul').append('<li><a id="offline-nav-next" href="#">&#8250;</a></li><li><a id="offline-nav-last" href="#">&#187;</a></li>');
    
    // Clicky!
    $('#offline-nav .active a').trigger('click');
}