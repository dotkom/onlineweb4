function ArticleWidget (Utils){
    ArticleWidget.prototype.render = function(callback) {
        callback = callback || function () {};

         // Loading featured
        Utils.makeApiRequest({
            'url': '/api/v1/articles/?format=json',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var articles = data.results;
                var len = (articles.length > 8) ? 8 : articles.length;
                if (len > 0) {
                    var output_featured = '';
                    var output_normal = '';

                    // The loop
                    for (var i = 0; i < len; i++) {

                        // Temporary replacement during the transition from Filebrowser to ResponsiveImage
                        if (!articles[i].image) {
                            articles[i].image = ''
                        }
                        
                        if (i <= 1) {
                            output_featured += '<div class="col-md-6"><a href="/article/'+articles[i].id+'/'+articles[i].slug+'"><img src="'+articles[i].image.sm+'" alt="'+articles[i].heading+'"><h3>'+articles[i].heading+'</h3></a><p>'+articles[i].ingress_short+'</p></div>';
                        }
                        else {
                            output_normal += '<div class="col-xs-6 col-md-2"><a href="/article/'+articles[i].id+'/'+articles[i].slug+'"><img src="'+articles[i].image.thumb+'" alt="'+articles[i].heading+'"><br /><h4>'+articles[i].heading+'</h4></a></div>';

                            // adds a separator to clear the floats in movile view
                            // #article-frontpage-normal @media (max-width: 991px) { div:nth-child(even) { .clearfix(); } }
                            // won't do magic afaik
                            if (i % 2 !== 0) {
                              output_normal += '<div class="article-widget-mobile-view-separator"></div>';
                            }
                        }
                    }

                    // Appending
                    $('#article-frontpage-featured').html(output_featured);
                    $('#article-frontpage-normal').html(output_normal);
                }
                else {
                    $('#article-frontpage-featured').html('<div class="col-md-12"><p class="ingress">Ingen artikler funnet</p></div>');
                }

                // Calling the callback
                callback();
            }
        });

    };
}
