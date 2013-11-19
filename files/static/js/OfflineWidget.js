function OfflineWidget (Utils){
    var that = $(this);
    this.data = {};
    /* Render the widget */
    OfflineWidget.prototype.render = function() {
        Utils.makeApiRequest({
            'url': '/api/v0/offline/issues/?format=json',
            'method': 'GET',
            'data': {},
            success: function(data) {
                that.data = data;
                OfflineWidget.prototype.createDom();
            }
        });
    };

    /* Create the DOM */
    OfflineWidget.prototype.createDom = function () {
        console.log($('.carousel-inner').width());
        var data = that.data;
        var prefix = $("#offlineCarousel").data("prefix");
        var suffix = '.thumb.png';
        var itemWrapperStart = '<div class="item centered">';
        var itemWrapperEnd = '</div>';
        var insertMe = '';
        var maxWidth = $('.carousel-inner').width();
        var maxWidthPer = 170;
        var issuesPerSlide = Math.floor(maxWidth/maxWidthPer);
        
        if (data.objects.length <= 0) {
            // No issues added
            insertMe += '<p>Ingen utgaver funnet.</p>';
        } else {
            // Create DOM for issues.
            for (var i = 0; i < data.objects.length; i++) {
                if(i === 0) {
                    insertMe += itemWrapperStart;
                }
                insertMe += '<a href="'+prefix+data.objects[i].issue+'"><img src="'+prefix+data.objects[i].issue+suffix+'" /></a>';

                if (i === data.objects.length - 1 || (i + 1) % issuesPerSlide === 0) {
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
    };

    // Recreate DOM on resize
    $(window).on('debouncedresize',function() {
        OfflineWidget.prototype.createDom();
    });
}
