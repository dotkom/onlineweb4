
$(function()
{
    $('.dropdown-toggle').dropdown();

    $('.btn-auth').click(function(e) {
        e.preventDefault();
        window.location = $(this).data('url');
    });

});
