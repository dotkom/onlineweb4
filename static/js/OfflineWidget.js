function OfflineWidget (Utils){
    var that = $(this);
    
    /* Render the widget */
    OfflineWidget.prototype.render = function(imageWidth, imageMargin) {
        Utils.makeApiRequest({
            'url': '/api/v0/offline/issues/?format=json',
            'method': 'GET',
            'data': {},
            success: function(data) {
                // Get the amount of images that would fit inside the widget.
                var imageCount = Math.floor($("#offlineCarousel").width() / imageWidth);
                // Now account for margin.
                // See #offlineCarousel .item a:not(:first-child) margin-left
                imageMargin = imageMargin*(imageCount-1);
                imageCount = Math.floor(($("#offlineCarousel").width() / (imageWidth+imageMargin)));
                
                var prefix = $("#offlineCarousel").data("prefix");
                var suffix = '.thumb.png';
                var itemWrapperStart = '<div class="item centered">';
                var itemWrapperEnd = '</div>';
                var insertMe = '';
                
                if (data.objects.length <= 0) {
                    // No issues added
                    insertMe += '<p>Ingen utgaver funnet.</p>';
                } else {
                    // Create DOM for issues.
                    for (var i = 0; i < data.objects.length; i++) {
                        if(i == 0) {
                            insertMe += itemWrapperStart;
                        }
                        insertMe += '<a href="'+prefix+data.objects[i].issue+'"><img src="'+prefix+data.objects[i].issue+suffix+'" /></a>';

                        if (i == data.objects.length - 1 || (i + 1) % imageCount == 0) {
                            insertMe += itemWrapperEnd;
                            if (i != data.objects.length - 1) {
                                insertMe += itemWrapperStart;
                            }
                        }
                    }
                }
                
                $("#offlineCarousel .carousel-inner").html(insertMe);
                $("#offlineCarousel .carousel-inner div.item:first").addClass("active");
                $("#offlineCarousel").carousel('pause');
            }
        });
    };
}
