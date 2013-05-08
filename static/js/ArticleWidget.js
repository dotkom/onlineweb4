function ArticleWidget (Utils){
    // My variables
    var elm_per_page = 9; // Number of elements we are loading at the same time
    var is_more_elements = true; // True if we have more elements, false if not. To avoid many empty ajax-calls
    var pre_query = ''; // The previous query made by the settings supplied
    
    /* Render the widget */
    ArticleWidget.prototype.render = function(page, overwrite, settings, callback_func) {
        // Building the query
        var q = '';
        if (settings.year != null)
            q += '&year='+settings.year;
        if (settings.month != null)
            q += '&month='+settings.month;
        if (settings.tag != null)
            q += '&tag='+settings.tag;
        
        // We got a new query! Set new query and reset more_elements
        if (q != pre_query) {
            pre_query = q;
            is_more_elements = true;
        }
        
        // Only call the method if we have more elements
        if (is_more_elements) {
            // The api-call
            Utils.makeApiRequest({
                'url': '/api/v0/article/all/?format=json&offset='+((page-1)*elm_per_page)+'&limit='+elm_per_page+q, // Calcuating the offset, grabbing the limit and supplying the query from the settings
                'method': 'GET',
                'data': {},
                success: function(data) {
                    // Variables
                    var num = 1;
                    var output = '<div class="span12'+((page == 1 && !overwrite)?'':' hide')+'">'; // If we are not on the first page (and not using the filters), make the elements hidden to fade them in later
                    
                    // The loop
                    for (var i = 0; i < data.articles.length; i++) {
                        // The markup
                        output += '<div class="span4 article"><a href="'+data.articles[i].id+'"><img src="http://dev.optimuscrime.net/stuff/ftp/placeholdershit.png" style="width: 248px; height: 100px;" alt="" /></a><a href="'+data.articles[i].id+'"><h3>'+data.articles[i].heading+'</h3></a><p>'+data.articles[i].ingress+'</p><span class="date pull-right">'+data.articles[i].published_date+'</span><span></span></div>'
                        
                        // Every third element in a chunk
                        if (num % 3 == 0)
                            output += '</div><div class="span12"><hr />';
                    
                        // Increasing num!    
                        num++;
                    }
                    
                    // Checking to see if we have no more elements
                    if (i != elm_per_page) {
                        is_more_elements = false;
                    }
                
                    // Wrapping up the chunk
                    output += '</div>';
                    
                    // Appending the content. Either appending content or replacing it based on parameters supplied
                    if (overwrite) {
                        // We are overwriting existing articles
                        $(".article:visible").fadeOut(400,function () { // Fade out the visible ones
                            if ($(".article:animated").length === 0) { // When all the fading out is done, continue
                                $("#article_archive_container").html(output); // Appending content
                                $("#article_archive_container .hide").fadeIn(400); // Aaaand finally fading in again
                            }
                        });
                    }
                    else {
                        // We are just appending articles
                        $("#article_archive_container").append(output);
                        
                        // If we are not on the first page, animate them in!
                        if (page != 1) {
                            $("#article_archive_container .hide").fadeIn(400);
                        }
                    }
                    
                    // If supplied a callback function, execute it
                    if (callback_func instanceof Function) {
                        callback_func();
                    }
                }
            });
        }
        else {
            if (callback_func instanceof Function) {
                callback_func();
            }
        }
    }
}