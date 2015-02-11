$(document).ready(function () {
    var handler = StripeCheckout.configure({
        key: 'pk_test_6pRNASCoBOKtIshFeQd4XMUh',
        image: '/square-image.png',
        token: function(token) {
            $.ajax({
              type: "POST",
              url: "/payment/{{ payment.id }}/{{ event.id }}/",
              data: "{requestToken: " + token + "}",
              success: success,
              dataType: dataType
            });
        }
    });

    $('#customButton').on('click', function(e) {
        // Open Checkout with further options
        handler.open({
            name: 'Online',
            description: '2 widgets ($20.00)',
            amount: 2000
        });
        e.preventDefault();
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function() {
        handler.close();
    });
});