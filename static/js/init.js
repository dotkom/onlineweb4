
$(function()
{
    $('.dropdown-toggle').dropdown();
    offlineWidget = new OfflineWidget(Utils);
    offlineWidget.render();
});

