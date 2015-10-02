function EventWidget (Utils){

    var that = $(this);

    /* Render the widget */
    EventWidget.prototype.render = function(callback) {
        callback = callback || function () {};

        var now = moment();

        Utils.makeApiRequest({
            'url':'/api/v1/events/?event_end__gte=' + now.format('YYYY-MM-DD') + '&ordering=event_start&format=json',
            'method' : 'GET',
            'data': {},
            success: function (data) {
                var events = data.results;
                var len = (events.length > 8) ? 8 : events.length;

                if (len > 0) {

                    // Fragment to append and global rowNode
                    var fragment = document.createDocumentFragment();
                    var eventList = $('<ul class="event-list clearfix"></ul>');
                    var rowNode;

                    $.each(events, function (index) {
                        // If the index is even, create a row and append item. Else just append item to row.
                        // (This is to distribute items left and right)
                        if (index >= 8) { return } // stop adding events if we're past 8
                        if (index < 2) {
                            if (index % 2 === 0) {
                                var htmlRow = '<div class="row clearfix hero"></div>';
                                rowNode = fragment.appendChild($(htmlRow)[0]);
                            }

                            rowNode.appendChild($(createEventItem(this))[0]);
                        }
                        else {
                            eventList.append($(createEventListitem(this))[0]);
                        }
                    });

                    rowNode = fragment.appendChild($('<div class="row clearfix hero"></div>')[0]);
                    rowNode.appendChild($(eventList)[0]);

                    // Append the fragment after processing rows
                    $('#event-items').append(fragment);

                    if ($('li', eventList).length % 2 === 0) {
                      $($('li', eventList)[$('li', eventList).length-2]).addClass('column-bottom');
                    }
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
    };

     /* Private function to create a string which represents an event item.
     * @param json object
     * @return string
     */
    function createEventItem(item) {
        var event_image = item.images[0];
        if ($(window).innerWidth() < 768) {
            event_image = item.images[1];
        }
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
        if(item.images.length > 0) {
            html +=             '<div class="item active">';
            html +=                 '<a href="events/' + item.id + '/' + item.slug + '">';
            html +=                         '<img src="' + event_image + '" width="100%" alt="" >';
            html +=                 '</a>';
            html +=             '</div>';
        }
        for(var i=0; i < item.company_event.length; i++){
            html +=         '<div class="item ' + (!item.images[0] && i === 0 ? 'active' : '') + '">';
            html +=             '<a href="events/' + item.id + '/' + item.slug + '">';
            html +=                 '<img src="' + item.company_event[i].companies.old_image_companies_thumb + '" width="100%" alt="" />';
            html +=             '</a>';
            html +=         '</div>';
        }
        html +=         '</div>';
        html +=     '</div>';
        html +=     '<span class="hero-date">' + moment(item.event_start).lang('nb').format('DD. MMMM') + '</span>';
        html += '</div></div>';

        return html;
    }

    function createEventListitem (item) {
        return '<li><span>'+moment(item.event_start).lang('nb').format('DD.MM')+'</span><a href="events/' + item.id + '/' + item.slug + '">'+item.title+'</a></li> ';
    }
}
