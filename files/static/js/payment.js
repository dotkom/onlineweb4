
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

var setupButton = function(data, price_id){

    var handler = StripeCheckout.configure({
        key: data['stripe_public_key'],
        image: '/static/img/online_stripe_logo.png',
        token: function(token) {
            $.ajax({
                type:"POST",
                url:"/payment/",
                data: {
                    'stripeToken': token.id,
                    'paymentId': data['payment_id'],
                    'priceId': price_id
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

    var buttonId = "#stripeButton" + price_id

    $(buttonId).on('click', function(e) {
        // Open Checkout with further options
        handler.open({
            name: 'Online',
            description: data['description'],
            amount: data[price_id]['stripe_price'],
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
    $.get( "/payment/payment_info/", function( data ) {
        for(var i = 0; i < data['price_ids'].length; i++){
            setupButton(data, data['price_ids'][i])
        }
    });
}


$(document).ready(function () {

    setupAjaxCSRF();
    setupPayment();
});
