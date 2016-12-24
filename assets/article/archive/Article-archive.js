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
        archive: true,
        year: null,
        month: null,
        tag: null,
        tagPage: 1
    };  // Object that holds the settings we are building an query from

    //
    // Here goes the code
    //

    // New ArticleWidget-class
    var articleWidget = new ArticleArchive(utils);

    // The initial rendgering (loading from ajax)
    // Build settings by url
    var pathname = window.location.pathname;
    var url = pathname.split('/');
    if (url[url.length-2] === 'month') {
        articleSettings.month = url[url.length-1];
        articleSettings.year  = url[url.length-3];
    } else if (url[url.length-2] === 'year') {
        articleSettings.year = url[url.length-1];
    } else if (url[url.length-3] === 'tag') {
        articleSettings.tag = url[url.length-2];
    }
    articleWidget.render(1,false,articleSettings);

    //
    // Method for infinite scrolling
    //

    var is_more_elements = true;

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
                is_more_elements = articleWidget.render(page,false,articleSettings,function () {
                    // Setting loading to false, so we can load another round later
                    is_loading_new_content = false;
                    if (articleSettings.tag)
                        articleSettings.tagPage++
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

            // Set buzy to true so we don't load multiple articles at once
            is_loading_new_content = true;

            var $obj = $(this);

            // Getting the tag-slug (had to be done using the url…
            var url = $obj.attr('href').split('/');

            // Updating the settings
            articleSettings.year = null;
            articleSettings.month = null;
            articleSettings.tag = url[url.length-2];
            articleSettings.tagPage = 1;


            page = 1;

            // Render!
            articleWidget.render(1,true,articleSettings,function () {
                // Setting loading to false, so we can load another round later
                is_loading_new_content = false;
                articleSettings.tagPage++
            });
    });

    //
    // Resetting tag-filter
    //

    $('#article_archive_filter_reset').on('click',function(e) {

        if (e.preventDefault)
            e.preventDefault();
        else
            e.stop();


        // Set buzy to true so we don't load multiple articles at once
        is_loading_new_content = true;

        // Updating the settings
        articleSettings.year = null;
        articleSettings.month = null;
        articleSettings.tag = null;
        articleSettings.tagPage = 1;
        page = 1;



        // Render!
        articleWidget.render(1,true,articleSettings,function () {
            // Setting loading to false, so we can load another round later
            is_loading_new_content = false;
        });
    });
});

function ArticleArchive (Utils) {
    // My variables
    var elm_per_page = 9; // Number of elements we are loading at the same time
    var is_more_elements = true; // True if we have more elements, false if not. To avoid many empty ajax-calls
    var pre_query = ''; // The previous query made by the settings supplied

    moment.lang('no', {
        months: [
            "januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"
        ]
    });

    /* Render the widget */
    ArticleArchive.prototype.render = function(page, overwrite, settings, callback_func) {
        is_more_elements = true;



        // Building the query
        var q = '';
        if (settings.year != null)
            q += '&year='+settings.year;
        if (settings.month != null)
            q += '&month='+settings.month;


        // We got a new query! Set new query and reset more_elements

        if (q != pre_query) {

            pre_query = q;
            is_more_elements = true;
        }



        var _url_params = "?format=json";
        if (settings.tag) {

            _url_params += '&tags=' + settings.tag;
            _url_params += '&page=' + settings.tagPage
        }
        if (settings.year != null || settings.month != null) {
            _url_params += q
        }

        if (!settings.tag && !settings.year && !settings.month) {
            // If no filtering, use page supplied
            _url_params += '&page=' + page
        }


        // Only call the method if we have more elements
        if (is_more_elements) {
            // The api-call
            Utils.makeApiRequest({
                'url': '/api/v1/articles/' + _url_params,
                'method': 'GET',
                'data': {},
                success: function(data) {

                    // Variables
                    var num = 1;
                    var output = '';
                    var articles = data.results;
                    var _len = (settings.archive) ? 10 : 8;
                    var len = (articles.length > _len) ? _len : articles.length; // Set length of loop to 8 if num articles is more than 8.

                    // The loop
                    for (var i = 0; i < len; i++) {
                        // The markup

                        // Because not all images are responsiveimage yet,
                        // will be removed later
                        if (!articles[i].image) {
                            articles[i].image = ''
                        }

                        output += '<div class="row">';
                        output += '<div class="col-md-12 article'+((page == 1 && !overwrite)?'':' article-hidden')+'">';
                        output += '  <div class="row">';
                        output += '    <div class="col-md-4">';
                        output += '      <div class="row">';
                        output += '        <a href="/article/'+articles[i].id+'/'+articles[i].slug+'">';
                        output += '          <img src="'+articles[i].image.sm+'" width="100%" alt="'+articles[i].heading+'" />';
                        output += '        </a>';
                        output += '      </div><!-- end row -->';
                        output += '    </div><!-- end col-md-4 -->';
                        output += '    <div class="col-md-8">';
                        output += '      <div class="pull-right article-detail-meta">';
                        output += '        <span>'+moment(articles[i].published_date).format('DD.MM.YYYY')+'</span>';
                        output += '      </div>';
                        output += '      <a href="/article/'+articles[i].id+'/'+articles[i].slug+'"><h3>'+articles[i].heading+'</h3></a>';
                        output += '      <p>'+articles[i].ingress_short+'</p>';
                        output += '      <div class="meta"><div class="row"><div class="col-md-12">';
                        output += '        <p><strong>Skrevet av: </strong>' + articles[i].authors + '</p>';
                        output += '      </div></div></div>';
                        output += '    </div><!-- end col-md-8 -->';
                        output += '  </div><!-- end row -->';
                        output += '</div><!-- end col-md-12 -->';
                        output += '</div><!-- end row -->';

                        // Increasing num!
                        num++;
                    }


                    // Checking to see if we have no more elements

                    is_more_elements = data.next != null;


                    // Wrapping up the chunk
                    output += '</div>';

                    // Appending the content. Either appending content or replacing it based on parameters supplied
                    if (overwrite) {
                        // We are overwriting existing articles
                        if ($(".article:visible").length > 0) {
                            $(".article:visible").fadeOut(400,function () { // Fade out the visible ones
                                if ($(".article:animated").length === 0) { // When all the fading out is done, continue
                                    $("#article_archive_container").html(output); // Appending content
                                    $("#article_archive_container .article-hidden").fadeIn(400); // Aaaand finally fading in again
                                }
                            });
                        }
                        else {
                            $("#article_archive_container").html(output); // Appending content
                            $("#article_archive_container .article-hidden").fadeIn(400); // Aaaand finally fading in again
                        }
                    }
                    else {
                        // We are just appending articles
                        $("#article_archive_container").append(output);

                        // If we are not on the first page, animate them in!
                        if (page != 1) {
                            $("#article_archive_container .article-hidden").fadeIn(400);
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
    };
}
