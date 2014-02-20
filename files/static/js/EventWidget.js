function EventWidget (Utils){

    var that = $(this);

    // 4 hero items by default
    // Divisible by 12 or die
    var amountOfHeroItems = 4;
    var maxHeroItemsPerRow = 4;

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

                    // Determine amount of hero items
                    if(data.events.length < amountOfHeroItems) {
                        amountOfHeroItems = data.events.length;
                    }

                    // Cut out hero items from the array we received from API
                    var heroItems = data.events.splice(0, amountOfHeroItems);

                    // Append hero items
                    $.each(heroItems, function(index) {
                        if(index % maxHeroItemsPerRow == 0) {
                            var htmlRow = '<div class="row clearfix hero"></div>';
                            rowNode = fragment.appendChild($(htmlRow)[0]);

                            var htmlItem = createEventItem(this);
                            rowNode.appendChild($(htmlItem)[0]);
                        }
                        else {
                            var htmlItem = createEventItem(this);
                            rowNode.appendChild($(htmlItem)[0]);
                        }
                    });

                    // Append list items
                    $.each(data.events, function (index) {
                        if(index % 2 == 0) {
                            var htmlItem = createEventListitem(this);
                            $(col1).append($(htmlItem)[0]);
                        }
                        else {
                            var htmlItem = createEventListitem(this);
                            $(col2).append($(htmlItem)[0]);
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

        var col_width = Math.floor(12 / amountOfHeroItems);
        var event_image = item.image_events_main;

        if ($(window).innerWidth() < 768) {
            event_image = item.image_events_thumb;
        }

        var html = '<div>';

        html =  '<div class="col-xs-12 col-md-8 col-lg-' + col_width + '">';
        html +=     '<div class="row">';
        html +=         '<div class="col-md-12" id="eventimage">';
        html +=             '<div id="event-carousel" class="carousel slide">';
        html +=                 '<div class="carousel-inner">';
        if(item.image_events_thumb) {
            html +=                 '<div class="item active">';
            html +=                     '<a href="events/' + item.id + '/' + item.slug + '">';
            html +=                         '<img src="' + event_image + '" width="100%" alt="" >';
            html +=                     '</a>';
            html +=                 '</div>';
        }
//        for(var i=0; i < item.company_event.length; i++){
//            html +=                 '<div class="item ' + (item.image_events_main ? '' : 'active') + '">';
//            html +=                     '<a href="events/' + item.id + '/' + item.slug + '">';
//            html +=                         '<img src="' + item.company_event[i].companies.image_companies_main + '" width="100%" alt="" />';
//            html +=                     '</a>';
//            html +=                 '</div>';
//        }
        html +=                 '</div>';
        html +=             '</div>';
        html +=         '</div>';
        html +=     '</div>';
        html +=     '<div class="row">';
        html +=         '<div class="col-xs-12 col-md-12" id="eventdescription">';
        html +=             '<div class="hero-title">';
        html +=                 '<a href="events/' + item.id + '/' + item.slug + '">';
        html +=                     '<p>' + item.title + '</p>';
        html +=                 '</a>';
        html +=             '</div>';
        html +=             '<div class="hero-ingress">';
        html +=                 '<p>' + item.ingress_short + '</p>';
        html +=             '</div>';
        html +=         '</div>';
        html +=     '</div>';
        html += '</div>';
        html += '</div>';

//        html = '<div>';
//        html +=   '<div class="col-sm-8 col-md-' + col_width + '" id="eventdescription">';
//        html +=       '<div class="hero-title">';
//        html +=           '<a href="events/' + item.id + '/' + item.slug + '">';
//        html +=               '<p>' + item.title + '</p>';
//        html +=           '</a>';
//        html +=       '</div>';
//        html +=       '<div class="hero-ingress hidden-xs">';
//        html +=           '<p>' + item.ingress_short + '</p>';
//        html +=       '</div>';
//        html +=   '</div>';
//        html += '<div class="col-sm-4 col-md-2" id="eventimage">';
//        html +=     '<div id="event-carousel" class="carousel slide">';
//        html +=         '<div class="carousel-inner">';
//        if(item.image_events_thumb) {
//            html +=             '<div class="item active">';
//            html +=                 '<a href="events/' + item.id + '/' + item.slug + '">';
//            html +=                         '<img src="' + event_image + '" width="100%" alt="" >';
//            html +=                 '</a>';
//            html +=             '</div>';
//        }
//        for(var i=0; i < item.company_event.length; i++){
//            html +=         '<div class="item ' + (item.image_events_thumb ? '' : 'active') + '">';
//            html +=             '<a href="events/' + item.id + '/' + item.slug + '">';
//            html +=                 '<img src="' + item.company_event[i].companies.image_companies_thumb + '" width="100%" alt="" />';
//            html +=             '</a>';
//            html +=         '</div>';
//        }
//        html +=         '</div>';
//        html +=     '</div>'
//        html +=     '<span class="hero-date">' + moment(item.event_start).lang('nb').format('DD. MMMM') + '</span>';
//        html += '</div></div>';

        return html;
    }
//    function createEventItem(item) {
//
//        var event_image = item.image_events_thumb;
//        if ($(window).innerWidth() < 768) {
//            event_image = item.image_events_main;
//        }
//        html = '<div><div class="col-sm-8 col-md-4" id="eventdescription">';
//        html +=     '<div class="hero-title">';
//        html +=         '<a href="events/' + item.id + '/' + item.slug + '">';
//        html +=             '<p>' + item.title + '</p>';
//        html +=         '</a>';
//        html +=     '</div>';
//        html +=     '<div class="hero-ingress hidden-xs">';
//        html +=         '<p>' + item.ingress_short + '</p>';
//        html +=     '</div>';
//        html += '</div>';
//        html += '<div class="col-sm-4 col-md-2" id="eventimage">';
//        html +=     '<div id="event-carousel" class="carousel slide">';
//        html +=         '<div class="carousel-inner">';
//        if(item.image_events_thumb) {
//            html +=             '<div class="item active">';
//            html +=                 '<a href="events/' + item.id + '/' + item.slug + '">';
//            html +=                         '<img src="' + event_image + '" width="100%" alt="" >';
//            html +=                 '</a>';
//            html +=             '</div>';
//        }
//        for(var i=0; i < item.company_event.length; i++){
//            html +=         '<div class="item ' + (item.image_events_thumb ? '' : 'active') + '">';
//            html +=             '<a href="events/' + item.id + '/' + item.slug + '">';
//            html +=                 '<img src="' + item.company_event[i].companies.image_companies_thumb + '" width="100%" alt="" />';
//            html +=             '</a>';
//            html +=         '</div>';
//        }
//        html +=         '</div>';
//        html +=     '</div>'
//        html +=     '<span class="hero-date">' + moment(item.event_start).lang('nb').format('DD. MMMM') + '</span>';
//        html += '</div></div>';
//
//        return html;
//    }

    function createEventListitem (item) {
        return '<li><a href="events/' + item.id + '/' + item.slug + '">'+item.title+'</a><span>'+moment(item.event_start).lang('nb').format('DD.MM')+'</span></li> ';
    }
}
