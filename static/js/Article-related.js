$(function() {
    var utils = new Utils(); // Class for the Widget
    var articleLatest = new ArticleLatest(utils);
    
    // Loading the lastest articles from the api to display on the right
    articleLatest.renderLatest();
});

function ArticleLatest (Utils) {
    ArticleLatest.prototype.renderLatest = function() {
        Utils.makeApiRequest({
            'url': '/api/v0/article/all/?format=json&limit=6&featured=False',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var output = '';

                // The loop
                for (var i = 0; i < data.articles.length; i++) {
                    output += '<div class="row-fluid"><div class="span12"><a href="/article/'+data.articles[i].id+'"><img src="'+data.articles[i].image_article_front_small+'" alt="'+data.articles[i].heading+'"></a><br /><h4>'+data.articles[i].heading+'</h4></div></div>';
                }

                $('#article-detaill-latest').html(output);
            }
        });
    }
}