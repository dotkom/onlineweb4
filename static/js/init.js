
$(document).ready(function()
{
	$('.dropdown-toggle').dropdown();

    online = new Online();
    eventWidget = new EventWidget(online);

    eventWidget.render();
});

