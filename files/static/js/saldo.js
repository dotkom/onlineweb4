
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

    var amount = 100

    var handler = StripeCheckout.configure({
        key: data['stripe_public_key'],
        image: '/static/img/online_stripe_logo.png',
        token: function(token) {
            // Dispatch event allowing IsLoading component to show.
            document.dispatchEvent(new Event('ow4-long-xhr-start'));
            $.ajax({
                type:"POST",
                url:"/payment/saldo/",
                data: {
                    'stripeToken': token.id,
                    'amount': amount
                },
                //Reloads the page on error or success to show the message and update the site content.
                success: function(){
                    // Tell IsLoading-component that request ended.
                    document.dispatchEvent(new Event('ow4-long-xhr-end'));

                    location.reload();
                },
                error: function(result){
                    // Tell IsLoading-component that request ended.
                    document.dispatchEvent(new Event('ow4-long-xhr-end'));

                    location.reload();
                }
            });
        }
    });

    var buttonId = "#stripeButton"

    $(buttonId).on('click', function(e) {

        amount = $('#amount').find(":selected").text();
        // Open Checkout with further options
        handler.open({
            name: 'Online',
            description: data['description'],
            amount: amount * 100,
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
    $.get( "/payment/saldo_info/", function( data ) {
        setupButton(data)
    });
}


$(document).ready(function () {

    setupAjaxCSRF();
    setupPayment();
});
