
$(document).ready(function()
{
    $('.dropdown-toggle').dropdown();

    utils = new utils();
    eventWidget = new EventWidget();

    eventWidget.render();
});

