
$(function()
{
    $('.dropdown-toggle').dropdown();


    Utils = new Utils();
    eventWidget = new EventWidget(Utils);
    eventWidget.render();

    articleWidget = new ArticleWidget(Utils);
    articleWidget.render();

    $('#filter-arrkom').on('click', function (e) {
        e.preventDefault();
        window.location = $(this).data('url');
    });

});
