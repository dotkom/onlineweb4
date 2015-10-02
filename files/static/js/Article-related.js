$(function() {
    $.ajax({
        'url': '/api/v1/articles/?format=json&featured=False',
        'method': 'GET',
        'data': {},
        success: function(data) {
            var output = '';
            var articles = data.results;
            var len = (articles.length > 6) ? 6 : articles.length; // Set length of loop to 6 if num articles is more than 6.
            
            // The loop
            for (var i = 0; i < len; i++) {
                output += '<div class="row-fluid"><div class="span12"><a href="/article/'+articles[i].id+'"><img src="'+articles[i].image.thumb+'" alt="'+articles[i].heading+'"></a><br /><h4>'+articles[i].heading+'</h4></div></div>';
            }
            
            // Appending
            $('#article-detaill-latest').html(output);
        }
    });
});
