$(function() {
    var articleWidget = new ArticleWidget(utils);
    
    // Loading the lastest articles from the api to display on the right
    articleWidget.renderLatest();
});