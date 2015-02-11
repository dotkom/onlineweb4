$(document).ready(function () {

    var data;

    $.get( "/payment/payment_info/", function( json ) {
      data = json;
    });


    var handler = StripeCheckout.configure({
        key: 'pk_test_6pRNASCoBOKtIshFeQd4XMUh',
        image: '/square-image.png',
        token: function(token) {
            $.ajax({
              type: "POST",
              url: "/payment/" + data['event_id'] + "/" + data['payment_id'] + "/",
              data: "{requestToken: " + token + "}"
            });
        }
    });

    $('#customButton').on('click', function(e) {
        // Open Checkout with further options
        handler.open({
            name: 'Online',
            description: data['description'],
            amount: data['stripe_priec'],
            email: data['email'],
            allowRememberMe: false,
            currency: "nok",
            panelLabel: "Betal " + data['price'] + "kr"

        });
        e.preventDefault();
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function() {
        handler.close();
    });
});