

$(document).ready(function () {
    /* AJAX SETUP FOR CSRF */
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    /* END AJAX SETUP */

    var data;

    $.get( "/payment/payment_info/", function( json ) {
      data = json;
    });


    var handler = StripeCheckout.configure({
        key: 'pk_test_6pRNASCoBOKtIshFeQd4XMUh',
        image: '',
        token: function(token) {
            var jsonToken = {};
            jsonToken.stripeToken = token

            console.log(token)

            $.ajax({
                 type:"POST",
                 url:"/payment/" + data['event_id'] + "/" + data['payment_id'] + "/",
                 data: {
                        'stripeToken': JSON.stringify(token)
                        },
                 success: function(){
                     //location.reload(true);
                    }
            });
            //$.post( "/payment/" + data['event_id'] + "/" + data['payment_id'] + "/", jsonToken.serialize());
        }
    });

    $('#customButton').on('click', function(e) {
        // Open Checkout with further options
        handler.open({
            name: 'Online',
            description: data['description'],
            amount: data['stripe_price'],
            email: data['email'],
            allowRememberMe: false,
            currency: "nok",
            panelLabel: "Betal "

        });
        e.preventDefault();
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function() {
        handler.close();
    });
});