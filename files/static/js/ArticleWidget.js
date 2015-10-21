function ArticleWidget (Utils){
    ArticleWidget.prototype.render = function(callback) {
        callback = callback || function () {};

         // Loading featured
        Utils.makeApiRequest({
            'url': '/api/v0/article/all/?format=json&limit=8',
            'method': 'GET',
            'data': {},
            success: function(data) {
                if (data.articles.length > 0) {
                    var output_featured = '';
                    var output_normal = '';

                    // The loop
                    for (var i = 0; i < data.articles.length; i++) {

                        // Temporary replacement during the transition from Filebrowser to ResponsiveImage
                        if (!data.articles[i].image) {
                            data.articles[i].image = ''
                        }
                        
                        if (i <= 1) {
                            output_featured += '<div class="col-md-6"><a href="/article/'+data.articles[i].id+'/'+data.articles[i].slug+'"><img src="'+data.articles[i].image.sm+'" alt="'+data.articles[i].heading+'"><h3>'+data.articles[i].heading+'</h3></a><p>'+data.articles[i].ingress_short+'</p></div>';
                        }
                        else {
                            output_normal += '<div class="col-xs-6 col-md-2"><a href="/article/'+data.articles[i].id+'/'+data.articles[i].slug+'"><img src="'+data.articles[i].image.thumb+'" alt="'+data.articles[i].heading+'"><br /><h4>'+data.articles[i].heading+'</h4></a></div>';

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
