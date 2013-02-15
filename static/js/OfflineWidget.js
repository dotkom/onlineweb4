function OfflineWidget (Utils){

    var that = $(this);
    
    /* Render the widget */
    OfflineWidget.prototype.render = function() {

        Utils.makeApiRequest({
            'url': '/api/v0/offline/issues/?format=json',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var maxCount = 3;
                var prefix = $("#offlineCarousel").data("prefix");
                var suffix = '.thumb.png';

                var itemWrapperStart = '<div class="item centered">';
                var itemWrapperEnd = '</div>';
                var appendMe = '';

                for (var i = 0; i < data.objects.length; i++) {
                    if(i == 0) {
                        appendMe += itemWrapperStart;
                    }

                    appendMe += '<a href="'+prefix+data.objects[i].issue+'"><img src="'+prefix+data.objects[i].issue+suffix+'" /></a>';

                    if(i == data.objects.length - 1 || (i + 1) % maxCount == 0) {
                        appendMe += itemWrapperEnd;
                        if(i != data.objects.length - 1) {
                            appendMe += itemWrapperStart;
                        }
                    }
                };

                $("#offlineCarousel .carousel-inner").append(appendMe);
                // Set active div.item
                $("#offlineCarousel .carousel-inner div.item:first").addClass("active");

            }
        });
    }
}
