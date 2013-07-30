function ArticleWidget (Utils){
    ArticleWidget.prototype.render = function() {
        // Loading featured
        Utils.makeApiRequest({
            'url': '/api/v0/article/all/?format=json&limit=2&featured=True',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var output = '';

                // The loop
                for (var i = 0; i < data.articles.length; i++) {
                    output += '<div class="span6"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_featured+'" alt="'+data.articles[i].heading+'"></a><h3>'+data.articles[i].heading+'</h3><p>'+data.articles[i].ingress+'</p></div>';
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
                    output += '<div class="span2"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_small+'" alt="'+data.articles[i].heading+'"></a><br /><h4>'+data.articles[i].heading+'</h4></div>';
                }

                $('#article-frontpage-normal').html(output);
            }
        });
    }
}
