function ArticleWidget (Utils){
    ArticleWidget.prototype.render = function(callback) {
         // Loading featured
        Utils.makeApiRequest({
            'url': '/api/v0/article/all/?format=json&limit=8',
            'method': 'GET',
            'data': {},
            success: function(data) {
                if(data.articles.length > 0) {
                    var output_featured = '';
                    var output_normal = '';

                    // The loop
                    for (var i = 0; i < data.articles.length; i++) {
                        if (i <= 1)
                            output_featured += '<div class="col-md-6"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_featured+'" alt="'+data.articles[i].heading+'"><h3>'+data.articles[i].heading+'</h3></a><p>'+data.articles[i].ingress+'</p></div>';
                        else
                            output_normal += '<div class="col-md-2"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_small+'" alt="'+data.articles[i].heading+'"><br /><h4>'+data.articles[i].heading+'</h4></a></div>';
                    }
                    
                    // Appending
                    $('#article-frontpage-featured').html(output_featured);
                    $('#article-frontpage-normal').html(output_normal);

                }else {
                    $('#article-frontpage-featured').html('<div class="col-md-12"><p class="ingress">Ingen artikler funnet</p></div>');
                }
                
                // Calling the callback
                callback();
            }
        });
        
        /*
        
        // Loading featured
        Utils.makeApiRequest({
            'url': '/api/v0/article/all/?format=json&limit=2&featured=True',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var output = '';

                // The loop
                for (var i = 0; i < data.articles.length; i++) {
                    output += '<div class="span6"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_featured+'" alt="'+data.articles[i].heading+'"></a><h3><a href="/article/'+data.articles[i].id+'">'+data.articles[i].heading+'</a></h3><p>'+data.articles[i].ingress+'</p></div>';
                }

                $('#article-frontpage-featured').html(output);
            }
        });

        // Loading "normal" articles
        Utils.makeApiRequest({
            'url': '/api/v0/article/all/?format=json&limit=6&featured=False',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var output = '';

                // The loop
                for (var i = 0; i < data.articles.length; i++) {
                    output += '<div class="span2"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_small+'" alt="'+data.articles[i].heading+'"></a><br /><h4><a href="/article/'+data.articles[i].id+'">'+data.articles[i].heading+'</a></h4></div>';
                }

                $('#article-frontpage-normal').html(output);
            }
        });
        
        */
    }
}
