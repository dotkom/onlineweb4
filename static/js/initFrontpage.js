
$(function()
{
    var utils = new Utils();
    var eventWidget = new EventWidget(utils);
    var offlineWidget = new OfflineWidget(utils)

    eventWidget.render();
    offlineWidget.render();

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

