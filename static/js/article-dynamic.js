$(function() {
    //
    // Varables
    //
    
    var justInited = false;
    var utils = new Utils(); // Class for the Widget
    var is_loading_new_content = false; // Indicating if we are currently loading something
    var page = 1; // What page we are on
    var months = {januar:1,februar:2,mars:3,april:4,mai:5,juni:6,juli:7,august:8,september:9,oktober:10,november:11,desember:12}; // Should be selfexplaining what this is
    var articleSettings = {
        year: null,
        month: null,
        tag: null} // Object that holds the settings we are building an query from
    
    //
    // Here goes the code
    //
    
    // New ArticleWidget-class
    var articleWidget = new ArticleWidget(utils);
    
    // The initial rendgering (loading from ajax)
    articleWidget.render(1,false,articleSettings);
    
    //
    // Method for infinite scrolling
    //
    
    $(document).on('scroll',function() {
        // If we are 10px from the bottom, execute new render
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            // Checking to see if we are curently buzy
            if (!is_loading_new_content) {
                // Set buzy to true so we don't load multiple articles at once
                is_loading_new_content = true;
                
                // Increasing page
                page++;
                
                // Do the actuall call with supplied callback
                articleWidget.render(page,false,articleSettings,function () {
                    // Setting loading to false, so we can load another round later
                    is_loading_new_content = false;
                });
            }
        }
    });
    
    //
    // Filtering articles on year (and perhaps month)
    //
    
    $('#article_archive_filter a').on('click',function(e) {
        // We don't want to rederect!!
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
        // Checking to see if buzy
        if (!is_loading_new_content) {
            // Set buzy to true so we don't load multiple articles at once
            is_loading_new_content = true;
            
            var $obj = $(this);
            
            // Setting page to 1 again
            page = 1;
            
            // Setting the urls correctly
            //window.history.pushState("", "Offline Archive", $obj.attr('href'));
            
            // Updating the settings
            articleSettings.tag = null;
            if ($obj.data('year') != '' && typeof $obj.data('year') != 'undefined')
                articleSettings.year = $obj.data('year');
            else
                articleSettings.year = null;
            if ($obj.data('month') != '' && typeof $obj.data('month') != 'undefined')
                articleSettings.month = months[$obj.data('month').toLowerCase()];
            else
                articleSettings.month = null;
            
            // Render!
            articleWidget.render(1,true,articleSettings,function () {
                // Setting loading to false, so we can load another round later
                is_loading_new_content = false;
            });
        }
    });
    
    //
    // Filtering articles on tags
    //
    
    $('#article_archive_tagcloud a').on('click',function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
         // Checking to see if buzy
        if (!is_loading_new_content) {
            // Set buzy to true so we don't load multiple articles at once
            is_loading_new_content = true;
            
            var $obj = $(this);
            
            // Getting the tag-slug (had to be done using the url…
            var url = $obj.attr('href').split('/');
            
            // Setting the urls correctly
            window.history.pushState("", "Offline Archive", $obj.attr('href'));
            
            // Updating the settings
            articleSettings.year = null;
            articleSettings.month = null;
            articleSettings.tag = url[url.length-1];
            page = 1;
            
            // Render!
            articleWidget.render(1,true,articleSettings,function () {
                // Setting loading to false, so we can load another round later
                is_loading_new_content = false;
            });
        }
    });
    
    //
    // Resetting tag-filter
    //
    
    $('#article_archive_tag_reset').on('click',function(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();
        
         // Checking to see if buzy
        if (!is_loading_new_content) {
            // Set buzy to true so we don't load multiple articles at once
            is_loading_new_content = true;
            
            // Updating the settings
            articleSettings.year = null;
            articleSettings.month = null;
            articleSettings.tag = null;
            page = 1;
            
            // Setting the urls correctly
            window.history.pushState("", "Offline Archive", $(this).attr('href'));
            
            // Render!
            articleWidget.render(1,true,articleSettings,function () {
                // Setting loading to false, so we can load another round later
                is_loading_new_content = false;
            });
        }
    });
});