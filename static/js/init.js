
$(document).ready(function()
{
    $('.dropdown-toggle').dropdown();

    Utils = new Utils();
    eventWidget = new EventWidget(Utils);

    eventWidget.render();
});

