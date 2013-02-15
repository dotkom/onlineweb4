
$(document).ready(function()
{
    $('.dropdown-toggle').dropdown();


    Utils = new Utils();
    eventWidget = new EventWidget(Utils);

    eventWidget.render();

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

    offlineWidget = new OfflineWidget(Utils);
    offlineWidget.render();
});

