/*
    Written by: Thomas Gautvedt with the help of God, Jesus and the rest of my friends at the zoo
    License: to kill
    Owner: Online
    Descrition: Welcome to epic hardcore javascript that ended up 10 times more complicated than it should…
    Encouragement: ENJOY!
*/

// Variables for the people
var buzy = false; // Please wait….!"/&"&/"&/"
var offline_num_in_row = 1; // Number of issues in a single row (may change on resize)
var offline_total_rows = 1; // Number of total rows (calculated based on the number of total issues to display)
var num_issues_to_display = 8; // Number of total issues
var num_issues_to_display_max = num_issues_to_display; // Don't ask...
var offline_num_in_row_previous = 1337; // The previous number of total issues

// jQuery goes here!
$(function() {
    // Clicking years to filter issues
    $('.filter-year').on('click', function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        // Showing the reset-shiiiiit
        if ($('#filter-reset').is(':hidden')) {
            $('#filter-reset').fadeIn(400);
        }
        
        // Check if currently animating
        if (!buzy) {
            // Swap classes
            $("#nav-header .active").removeClass("active");
            $(this).parent().addClass("active");
            
            // The sort
            filter($(this).html());
        }
    });
    
    // Clearing the filter
    $('#filter-reset').on('click', function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        // Hide the reset-shit
        $('#filter-reset').fadeOut(400);
        
        // Checking if currently animated and filter is set
        if (!buzy && $('#nav-header .active').length != 0) {
            // Resetting issues to display
            num_issues_to_display = num_issues_to_display_max;
            
            // Removing active menu-point
            $('#nav-header .active').removeClass('active');
            
            // Adding displayable to all issues
            $('.offline_issue').each(function() {
                $obj = $(this);
                if (!$obj.hasClass('displayable'))
                    $obj.addClass('displayable');
            });
            
            // …and finally initing the display-function
            init_offline(true);
        }
    });
    
    // Click on the nav-buttons (arrows and numbers
    $('#offline-nav').on('click','a',function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        // Can I has zhe object
        var $obj = $(this);
        
        // Doing stuff if nonmongo-user
        if (!$obj.parent().hasClass('disabled')) {
            // Pre-selected index
            var selected_index = parseInt($('#offline-nav ul li.active a').attr('id').split('-')[1]);
            
            // Getting selected_index
            if ($obj.hasClass('offline-nav')) {
                // The current nav-button is an indexed one
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
            
            // Hide all the visible issues and fade in the new ones
            var num = 0;
            if ($('.offline_issue:visible').length > 0) {
                // We can run an animation here
                $('.offline_issue:visible').fadeOut(400,function () {
                    if ($(".offline_issue:animated").length === 0) {
                        // Done fading out
                        $('.offline_issue.displayable').each(function() {
                            // Checking to see if this is one of the issues that we can display on the first page, or if this goes on the 2nd, 3rd … one
                            if (num >= (num_issues_to_display*parseInt(clicked_index)) && num < (num_issues_to_display*(parseInt(clicked_index)+1))) {
                                $(this).stop().fadeIn(400,function () {
                                    if ($(".displayable:animated").length === 0) {
                                        // All fading in is done, we're no longer busy!
                                        busy = false;
                                    }
                                });
                            }
                            
                            // Incr
                            num++;
                        });
                    }
                });
            }
            else {
                // There are no visible issues (is this even possible…?), so just fade 'em. Comments in section ^
                $('.offline_issue.displayable').each(function() {
                    if (num >= (num_issues_to_display*parseInt(clicked_index)) && num < (num_issues_to_display*(parseInt(clicked_index)+1))) {
                        $(this).fadeIn(400,function () {
                            if ($(".offline_issue.displayable:animated").length === 0) {
                                busy = false;
                            }
                        });
                    }
                    
                    num++;
                });
            }
            
            // Removing active
            $('#offline-nav .active').removeClass('active');
            
            // Setting new active
            $('.offline-nav').eq(clicked_index).parent().addClass('active');
            
            // Getting the current selected page-id
            var new_selected_index = $('#offline-nav ul li.active a').attr('id').split('-')[1];
            
            // Just checking if we have more than one page...
            if ($('.offline-nav').length > 1) {
                if (new_selected_index == 0) {
                    // First page! Set the left buttons disabled
                    $('#offline-nav-first').parent().addClass('disabled');
                    $('#offline-nav-prev').parent().addClass('disabled');
                
                    if ($('#offline-nav-next').parent().hasClass('disabled')) {
                        $('#offline-nav-next').parent().removeClass('disabled');
                        $('#offline-nav-last').parent().removeClass('disabled');
                    }
                }
                else if (new_selected_index == ($('.offline-nav').length-1)) {
                    // Last page! Set the frikking right buttons disabled
                    $('#offline-nav-next').parent().addClass('disabled');
                    $('#offline-nav-last').parent().addClass('disabled');
                
                    if ($('#offline-nav-prev').parent().hasClass('disabled')) {
                        $('#offline-nav-prev').parent().removeClass('disabled');
                        $('#offline-nav-first').parent().removeClass('disabled');
                    }
                }
            }
        }
    });
    
    // Resize container 'n shit
    init_offline(false);
    
    // Fikser paginator
    init_pageinator();
    
    // On resize (jusing jQuery-plugin for smart resizing to avoid 32948239842834 events firering at the same time)
    $(window).on("debouncedresize", init_offline(false));
});

// Function for filtering issues
function filter(year) {
    // Looping all issues
    $('.offline_issue').each(function () {
        $obj = $(this);
        
        // Adding/removing displayable on the issues depending on the filter's year
        if (parseInt(year) == parseInt($obj.data('year'))) {
            if (!$obj.hasClass('displayable'))
                $obj.addClass('displayable');
        }
        else {
            if ($obj.hasClass('displayable'))
                $obj.removeClass('displayable');
        }
    });
    
    // Aaaaand then we fix variables and fix the viewport/nav
    init_offline(true);
}

// Retarded function that mostly set variables we're using later on…aaand resizing the viewport of the container
function init_offline(state) {
    // Deciding how many issues we are actually dealing with
    if ($('.offline_issue.displayable').length > num_issues_to_display) {
        if ($('.offline_issue.displayable').length > num_issues_to_display_max)
            num_issues_to_display = num_issues_to_display_max;
        else
            num_issues_to_display = $('.offline_issue.displayable').length;
    }
    else {
        num_issues_to_display = $('.offline_issue.displayable').length;
    }
    
    // Number of issues in one row (this can change based on the width of the page)
    offline_num_in_row = parseInt(Math.floor($('#offline-wrapper').width()/182));

    // Getting how many rows we have to display at once to display the minimum number of issues
    var offline_rows_minimum = parseInt(Math.ceil(num_issues_to_display/offline_num_in_row));
    
    // Animating the height of the container
    $('#offline-wrapper').stop().animate({height: (offline_rows_minimum*230)},400);
    
    // Storing total number of rows with issues
    offline_total_rows = parseInt(Math.ceil($('.offline_issue.displayable').length/(offline_num_in_row*offline_rows_minimum)));
    
    // Checking if we need to trigger a click and repaint the menu
    if (offline_num_in_row_previous == 1337) // <- I know...
        offline_num_in_row_previous = offline_total_rows;
    else {
        if (offline_num_in_row_previous != offline_total_rows || state) { // <- I know, retarded solution
            offline_num_in_row_previous = offline_total_rows;
            
            // Redraw the nav
            init_pageinator();
        }
        else {
            offline_num_in_row_previous = offline_total_rows;
        }
        
    }
}

// Appending arrows and numbers to the navigation
function init_pageinator() {
    // Show/hide
    if (offline_total_rows == 1) {
        if ($('#offline-nav').is(':visible')) {
            $('#offline-nav').hide();
        }
    }
    else {
        if ($('#offline-nav').is(':hidden')) {
            $('#offline-nav').show();
        }
    }
    
    
    // Removing first
    $('#offline-nav ul.pagination').empty();
    
    // Last/prev
    $('#offline-nav ul.pagination').append('<li class="disabled"><a id="offline-nav-first" href="#">&#171;</a></li><li class="disabled paddright"><a id="offline-nav-prev" href="#">&#8249;</a></li>');
    
    // Nums
    for (var i = 0; i < offline_total_rows; i++) {
        $('#offline-nav ul.pagination').append('<li'+((i == 0)?' class="active first"':'')+'><a class="offline-nav" id="page-'+i+'" href="#">'+(i+1)+'</a></li>');
    }
    
    // Next/last
    console.log(offline_total_rows);
    $('#offline-nav ul.pagination').append('<li class="paddleft'+((offline_total_rows == 1)?' disabled':'')+'"><a id="offline-nav-next" href="#">&#8250;</a></li><li'+((offline_total_rows == 1)?' class="disabled"':'')+'><a id="offline-nav-last" href="#">&#187;</a></li>');
    
    // Clicky!
    $('#offline-nav .active a').trigger('click');
}
