function ArticleWidget (Utils){

    var that = $(this);
    
    /* Render the widget */
    ArticleWidget.prototype.render = function() {
        var now = moment();

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
    }

    /* Private function to append items to a list
     * @param jQuery-object
     */
    function renderArticleList(list, item) {
        // Fikser stort bilde
        img = item.image.split('.');
        //if (img.length > 1) {
        //    img[img.length-2] = img[img.length-2]+"_article_front_featured"
        //    item.image = img.join('.');
        //}
        list.append('<div class="span6"><a class="" href="#"><img src="/uploaded_media/'+ item.image +'" alt="" /></a><h3>'+ item.heading +'</h3><p>'+ item.ingress +'s</p></div>');
    }

    ArticleWidget.prototype.filter = function(flag) {
        // Check if reset or filter
        if(flag == 0) {
            $('.event-item').show();
        }else{
            $.when($('.event-item').show()).then(function() {
                $.each($('.event-item'), function(index, item) { 
                    if(!$(item).hasClass('bullet-'+ flag))
                        $(item).hide();
                });        
            }); 
        }
    }
}
