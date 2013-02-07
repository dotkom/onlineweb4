


function EventWidget (Utils){

    var that = $(this);
    
    /* Private static method */
    getBulletForEventType = function(type) {
        
        switch(type) {
            case 1:
                return 'arrkom';
            case 2:
                return 'bedkom';
            case 3:
                return 'fagkom';
            default:
                return 'arrkom';
        }
    };

    /* Render the widget */
    EventWidget.prototype.render = function() {
        var now = moment();

        Utils.makeApiRequest({
            'url':'/api/v0/events/?event_end__gte=' + now.format('YYYY-MM-DD') + '&order_by=event_start&limit=8&format=json',
            'method' : 'GET',
            'data': {},
            success: function(data) {
                if(data.events.length > 0) {
                    $.each(data.events, function(index, singleEvent) {

                        var date = moment(singleEvent.event_start);
                        var bulletType = getBulletForEventType(singleEvent.event_type) 

                        // Distribute four on each side
                        if(index < 4)
                            $('#event-right').append('<li><img src="/static/img/' + bulletType + '_bullet.png" />' + 
                                singleEvent.title + '<span class="dates">' + date.format('DD/MM') + '</span></li>');
                        else
                            $('#event-left').append('<li><img src="/static/img/' + bulletType + '_bullet.png" />' + 
                                singleEvent.title + '<span class="dates">' + date.format('DD/MM') + '</span></li>');
                    });
                }else{
                    // Display text if no data was found
                    $('#event-span-left').html('<p class="ingress">Ingen arrangementer funnet</p>');
                }
            }
        });
    };

    
}
