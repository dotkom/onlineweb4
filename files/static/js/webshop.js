var setupAjaxCSRF = function(){
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
}

var setupButton = function(data){

    amount = data['price']

    var handler = StripeCheckout.configure({
        key: data['stripe_public_key'],
        image: '/static/img/online_stripe_logo.png',
        token: function(token) {
            $.ajax({
                type:"POST",
                url:"/payment/webshop_pay/",
                data: {
                    'stripeToken': token.id,
                    'order_line_id': data['order_line_id'],
                    'amount': amount
                },
                //Reloads the page on error or success to show the message and update the site content.
                success: function(){
                    location.reload();
                },
                error: function(result){
                    location.reload();
                }
            });
        }
    });

    var buttonId = "#stripe-button"

    $(buttonId).on('click', function(e) {
        // Open Checkout with further options
        handler.open({
            name: 'Prokom',
            description: "Fullfør ordre",
            amount: amount,
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
}

var setupPayment = function(){
    $.get( "/payment/webshop_info/", function( data ) {
        setupButton(data)
    });
}


$(document).ready(function () {

    setupAjaxCSRF();
    setupPayment();
}); 