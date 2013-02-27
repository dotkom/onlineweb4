
$(function()
{
    var utils = new Utils();
    var eventWidget = new EventWidget(utils);
    var offlineWidget = new OfflineWidget(utils)

    // Render on load
    eventWidget.render();
    offlineWidget.render(156, 10);

    // Render on resize
    $(window).resize(function() {
        offlineWidget.render(156, 10);
    });
    
    // Enable tabbing in about section
    $('#about-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    // Hook up filter buttons in event section
    $('#filter-arrkom').on('click', function (e) {
        e.preventDefault();
        eventWidget.filter(1);
    });
    $('#filter-bedkom').on('click', function (e) {
        e.preventDefault();
        eventWidget.filter(2);
    });
    $('#filter-fagkom').on('click', function (e) {
        e.preventDefault();
        eventWidget.filter(3);
    });
    $('#filter-reset').on('click', function (e) {
        e.preventDefault();
        eventWidget.filter(0);
    });
});

