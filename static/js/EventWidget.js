


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
                    $.each(data.events, function(index, item) {

                        // Distribute four on each side
                        if(index < 4)
                            renderEventList($('#event-right'), item);
                        else
                            renderEventList($('#event-left'), item);
                    });
                }else{
                    // Display text if no data was found
                    $('#event-span-left').html('<p class="ingress">Ingen arrangementer funnet</p>');
                }
            }
        });
    }

    /* Private function to append items to a list
     * @param jQuery-object
     */
    function renderEventList(list, item) {
        list.append('<li class="event-item bullet-' + item.event_type + '">' + 
            item.title + '<span class="dates">' + moment(item.event_start).format('DD/MM') + '</span></li>');
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
