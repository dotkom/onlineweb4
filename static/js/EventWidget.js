


function EventWidget (online) {

    var that = $(this);


    EventWidget.prototype.render = function() {
        
        Online.makeApiRequest({
            'url':'/static/test.json',
            'method' : 'GET',
            'data': {},
            success: function(data) {
                console.log(data);
                $.each(data.events, function(index, singleEvent) {
                    $('.event_list').append('<li><a href="#">' + 
                        singleEvent.title + '</a><span>' + singleEvent.event_start + '</span></li>');
                    });
                }
        });
    };

}
