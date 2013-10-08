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
                            htmlRow = '<div class="row clearfix hero"></div>';
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
                $('.carousel').carousel();
                callback();
            }
        });
    }

     /* Private function to create a string which represents an event item.
     * @param json object
     * @return string
     */
    function createEventItem(item) {

        html = '<div><div class="col-md-4 col-xs-7">';
        html +=     '<div class="hero-title">';
        html +=         '<a href="events/' + item.id + '/' + item.slug + '">';
        html +=             '<p>' + item.title + '</p>';
        html +=         '</a>';
        html +=     '</div>';
        html +=     '<div class="hero-ingress hidden-xs">';
        html +=         '<p>' + item.ingress_short + '</p>';
        html +=     '</div>';
        html += '</div>';
        html += '<div class="col-xs-5 col-md-2">';
        html +=     '<div id="event-carousel" class="carousel slide">';
        html +=         '<div class="carousel-inner">';
        html +=             '<div class="item active">';
        html +=                 '<img src="' + item.image_events_thumb + '" width="100%" alt="" >';
        html +=             '</div>';
        for(var i=0; i < item.company_event.length; i++){
            html +=         '<div class="item">';
            html +=             '<img src="' + item.company_event[i].companies.image_companies_thumb + '" width="100%" alt="" />';
            html +=         '</div>';
        }
        html +=         '</div>';
        html +=     '</div>'
        html +=     '<span class="hero-date">' + moment(item.event_start).lang('nb').format('DD. MMMM') + '</span>';
        html += '</div></div>';

        return html;
    }
}
