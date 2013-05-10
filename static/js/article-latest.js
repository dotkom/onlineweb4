$(function() {
    var utils = new Utils(); // Class for the Widget
    var articleWidget = new ArticleWidget(utils);
    
    // Loading the lastest articles from the api to display on the right
    articleWidget.renderLatest();
});