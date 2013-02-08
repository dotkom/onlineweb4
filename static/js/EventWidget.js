


function EventWidget (Utils){

    var that = $(this);
    
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

                        // Distribute four on each side
                        if(index < 4)
                            $('#event-right').append('<li class="event-item bullet-' + singleEvent.event_type + '">' + 
                                singleEvent.title + '<span class="dates">' + date.format('DD/MM') + '</span></li>');
                        else
                            $('#event-left').append('<li class="event-item bullet-' + singleEvent.event_type + '">' + 
                                singleEvent.title + '<span class="dates">' + date.format('DD/MM') + '</span></li>');
                    });
                }else{
                    // Display text if no data was found
                    $('#event-span-left').html('<p class="ingress">Ingen arrangementer funnet</p>');
                }
            }
        });
    }

    EventWidget.prototype.filter = function(flag) {
        // Check if reset or filter
        if(flag == 0) {
            $('.event-item').show();
        }else{
            $.when($('.event-item').show()).then(function() {
                $.each($('.event-item'), function(index, item) { 
                    if(!$(item).hasClass('bullet-'+ flag))
                        $(item).hide();
                });        
            }); 
        }
    }
}
