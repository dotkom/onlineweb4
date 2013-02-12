
$(function()
{
    var utils = new Utils();
    eventWidget = new EventWidget(utils);

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
});

