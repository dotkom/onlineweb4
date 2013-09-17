function EventWidget (Utils){

    var that = $(this);

    /* Render the widget */
    EventWidget.prototype.render = function(callback) {
        var now = moment();

        Utils.makeApiRequest({
            'url':'/api/v0/events/?event_end__gte=' + now.format('YYYY-MM-DD') + '&order_by=event_start&limit=6&format=json',
            'method' : 'GET',
            'data': {},
            success: function(data) {
                if(data.events.length > 0) {

                    // Fragment to append and global rowNode
                    var fragment = document.createDocumentFragment();
                    var rowNode;

                    $.each(data.events, function(index) {

                        // If the index is even, create a row and append item. Else just append item to row.
                        // (This is to distribute items left and right)
                        if(index % 2 == 0) {
                            htmlRow = '<div class="row-fluid event-row"></div>';
                            rowNode = fragment.appendChild($(htmlRow)[0]);

                            htmlItem = createEventItem(this);
                            rowNode.appendChild($(htmlItem)[0]);
                        }else{
                            htmlItem = createEventItem(this);
                            rowNode.appendChild($(htmlItem)[0]);
                        }
                    });

                    // Append the fragment after processing rows
                    $('#event-items').append(fragment);

                }else{
                    // Display text if no data was found
                    $('#event-items').html('<p class="ingress">Ingen arrangementer funnet</p>');
                }
                
                // Calling the callback
                callback();
            }
        });
    }

     /* Private function to create a string which represents an event item.
     * @param json object
     * @return string
     */
    function createEventItem(item) {
        
        html = '<div class="span6">';
        html +=     '<div class="span1 event-type-' + item.event_type + '">';
        html +=         '<div class="row-fluid"><span class="event-calendar-date">' + moment(item.event_start).format('DD') + '</span></div>';
        html +=         '<div class="row-fluid"><span class="event-calendar-month">' + moment(item.event_start).format('MMM') + '</span></div>';
        html +=     '</div>';
        html += '<div class="span3"><a href="events/' + item.id + '/' + item.slug + '"><img src="' + item.image_events_thumb + '" alt="" /></a></div>';
        html +=     '<div class="span8">';
        html +=         '<a href="events/' + item.id + '/' + item.slug + '">';
        html +=             '<div class="event-title">' + item.title + '</div>';
        html +=         '</a>'
        html +=         '<div class="event-ingress">' + item.ingress_short + '</div>';
        html += '   </div>';
        html += '</div>';

        return html;
    }
}
