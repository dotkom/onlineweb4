
$(function()
{
    var utils = new Utils();
    var eventWidget = new EventWidget(utils);
    var offlineWidget = new OfflineWidget(utils);
    var articleWidget = new ArticleWidget(utils);

    // Render on load
    eventWidget.render();
    offlineWidget.render(156, 10);
	articleWidget.renderFrontpage();

    // Render on resize
    $(window).resize(function() {
        offlineWidget.render(156, 10);
    });

    // Enable tabbing in about section
    $('#about-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

});

