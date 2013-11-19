function EventWidget (Utils){

    var that = $(this);

    /* Render the widget */
    EventWidget.prototype.render = function(callback) {
        callback = callback || function () {};
        
        var now = moment();

        Utils.makeApiRequest({
            'url':'/api/v0/events/?event_end__gte=' + now.format('YYYY-MM-DD') + '&order_by=event_start&limit=10&format=json',
            'method' : 'GET',
            'data': {},
            success: function (data) {
                if (data.events.length > 0) {

                    // Fragment to append and global rowNode
                    var fragment = document.createDocumentFragment();
                    var col1 = $('<ul class="event-list col-sm-12 col-md-6"></ul>');
                    var col2 = $('<ul class="event-list col-sm-12 col-md-6"></ul>');
                    var rowNode;

                    $.each(data.events, function (index) {
                        // If the index is even, create a row and append item. Else just append item to row.
                        // (This is to distribute items left and right)
                        if (index < 2) {
                            if (index % 2 == 0) {
                                var htmlRow = '<div class="row clearfix hero"></div>';
                                rowNode = fragment.appendChild($(htmlRow)[0]);

                                var htmlItem = createEventItem(this);
                                rowNode.appendChild($(htmlItem)[0]);
                            }
                            else {
                                var htmlItem = createEventItem(this);
                                rowNode.appendChild($(htmlItem)[0]);
                            }
                        }
                        else {
                            if (index - 2 < (data.events.length - 2) / 2) {
                                var htmlItem = createEventListitem(this);
                                $(col1).append($(htmlItem)[0]);
                            }
                            else {
                                var htmlItem = createEventListitem(this);
                                $(col2).append($(htmlItem)[0]);
                            }
                        }
                    });

                    rowNode = fragment.appendChild($('<div class="row clearfix hero"></div>')[0]);
                    rowNode.appendChild($(col1)[0]);
                    rowNode.appendChild($(col2)[0]);

                    // Append the fragment after processing rows
                    $('#event-items').append(fragment);
                }
                else {
                    // Display text if no data was found
                    $('#event-items').html('<p class="ingress">Ingen arrangementer funnet</p>');
                }
                
                if ( ($($('.event-list')[0]).children().length <= 1 && $($('.event-list')[1]).children().length == 1) ||
                    ($($('.event-list')[0]).children().length == 1 && $($('.event-list')[1]).children().length <= 1)
                ) {
                    $('.event-list li').addClass('border');
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

        html = '<div><div class="col-sm-8 col-md-4" id="eventdescription">';
        html +=     '<div class="hero-title">';
        html +=         '<a href="events/' + item.id + '/' + item.slug + '">';
        html +=             '<p>' + item.title + '</p>';
        html +=         '</a>';
        html +=     '</div>';
        html +=     '<div class="hero-ingress hidden-xs">';
        html +=         '<p>' + item.ingress_short + '</p>';
        html +=     '</div>';
        html += '</div>';
        html += '<div class="col-sm-4 col-md-2" id="eventimage">';
        html +=     '<div id="event-carousel" class="carousel slide">';
        html +=         '<div class="carousel-inner">';
        if(item.image_events_thumb) {
            html +=             '<div class="item active">';
            html +=                 '<a href="events/' + item.id + '/' + item.slug + '">';
            html +=                         '<img src="' + item.image_events_thumb + '" width="100%" alt="" >';
            html +=                 '</a>';
            html +=             '</div>';
        }
        for(var i=0; i < item.company_event.length; i++){
            html +=         '<div class="item ' + (item.image_events_thumb ? '' : 'active') + '">';
            html +=             '<a href="events/' + item.id + '/' + item.slug + '">';
            html +=                 '<img src="' + item.company_event[i].companies.image_companies_thumb + '" width="100%" alt="" />';
            html +=             '</a>';
            html +=         '</div>';
        }
        html +=         '</div>';
        html +=     '</div>'
        html +=     '<span class="hero-date">' + moment(item.event_start).lang('nb').format('DD. MMMM') + '</span>';
        html += '</div></div>';

        return html;
    }

    function createEventListitem (item) {
        return '<li><a href="events/' + item.id + '/' + item.slug + '">'+item.title+'</a><span>'+moment(item.event_start).lang('nb').format('DD.MM')+'</span></li> ';
    }
}
