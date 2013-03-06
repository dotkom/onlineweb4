function ArticleWidget (Utils){

    var that = $(this);
    
    /* Render the widget */
    ArticleWidget.prototype.render = function() {
        // Laster featured
        Utils.makeApiRequest({
            'url':'/api/v0/article/latest?featured=True&limit=2&format=json',
            'method' : 'GET',
            'data': {},
            success: function(data) {
                if(data.articles.length > 0) {
                    $.each(data.articles, function(index, item) {
                        renderArticleList($('#articles_featured'), item);
                    });
                }
            }
        });

        // Laster non-featured
        Utils.makeApiRequest({
            'url':'/api/v0/article/latest?featured=False&limit=6&format=json',
            'method' : 'GET',
            'data': {},
            success: function(data) {
                if(data.articles.length > 0) {
                    $.each(data.articles, function(index, item) {
                        renderArticleList($('#articles_normal'), item);
                    });
                }
            }
        });
    }

    /* Private function to append items to a list
     * @param jQuery-object
     */
    function renderArticleList(list, item) {
        if (list.attr('id') == 'articles_featured') {
            // Fikser stort bilde
            item.image = resizeArticleImg(item.image,'article_front_featured');
        
            // Appender
            list.append('<div class="span6"><a href="/articles/'+ item.id +'/'+ item.slug +'"><img width="584" height="275" src="/uploaded_media/'+ item.image +'" alt="'+ item.heading +'" /></a><h3>'+ item.heading +'</h3><p>'+ item.ingress +'s</p></div>');
        }
        else {
            // Fikser lite bilde
            item.image = resizeArticleImg(item.image,'article_front_small');
            // Appender
            list.append('<div class="span2"><a href="/articles/'+ item.id +'/'+ item.slug +'"><img width="174" height="100" src="/uploaded_media/'+ item.image +'" alt="" /></a><h4>'+ item.heading +'</h4></div>');
        }
    }   

    function resizeArticleImg(url,version) {
        img = url.split('.');
        if (img.length > 1) {
            img[img.length-2] = img[img.length-2]+"_"+version
            return img.join('.');
        }
        else {
            return url;
        }
    }
}
