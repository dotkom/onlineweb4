$(document).ready(function() {

    // This small hack is needed to allow city to be fetched from bring.
    // On a request to bring, crossdomain needs to be set to false, and then restored when the request is fulfilled.

    var ext_setup = function() {
        $.ajaxSetup({
            crossDomain: true
        });
    }

    var ext_shutdown = function () {
        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                }
            }
        });
    }

    var loadCity = function() {
        var zipCode = $("#zip-code").text();
        ext_setup();
        $.ajax({
            url: 'https://fraktguide.bring.no/fraktguide/api/postalCode.json?country=no&pnr=' + zipCode + '&callback=?',
            dataType: "jsonp",
            success: function (res) {
                $("#city").html("&nbsp;" + res.result);
                ext_shutdown();
            },
            error: function (xhr, st, options) {
                ext_shutdown();
            }
        });
    };
    loadCity();
});