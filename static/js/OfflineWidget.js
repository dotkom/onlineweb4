function OfflineWidget (Utils){

    var that = $(this);
    
    /* Render the widget */
    OfflineWidget.prototype.render = function() {

        Utils.makeApiRequest({
            'url': '/api/v0/offline/issues/?format=json',
            'method': 'GET',
            'data': {},
            success: function(data) {
                var maxCount = Math.floor($("#offlineCarousel").width() / 156);
                var prefix = $("#offlineCarousel").data("prefix");
                var suffix = '.thumb.png';

                var itemWrapperStart = '<div class="item centered">';
                var itemWrapperEnd = '</div>';
                var insertMe = '';

                for (var i = 0; i < data.objects.length; i++) {
                    if(i == 0) {
                        insertMe += itemWrapperStart;
                    }
                    insertMe += '<a href="'+prefix+data.objects[i].issue+'"><img src="'+prefix+data.objects[i].issue+suffix+'" /></a>';

                    if(i == data.objects.length - 1 || (i + 1) % maxCount == 0) {
                        insertMe += itemWrapperEnd;
                        if(i != data.objects.length - 1) {
                            insertMe += itemWrapperStart;
                        }
                    }
                }

                $("#offlineCarousel .carousel-inner").html(insertMe);
                // Set active div.item
                $("#offlineCarousel .carousel-inner div.item:first").addClass("active");

            }
        });

    }
}
