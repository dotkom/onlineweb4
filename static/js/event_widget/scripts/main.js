define(function(require) {
    var Backbone = require('backbone');
    var EventCollection = require('event.collection');

    var EventWidget = Backbone.View.extend({
        el: '#main',

        initialize: function() {
            var events = new EventCollection();
            events.fetch().done(function(response) {
                console.log(response);
                console.log(events);
            });
        }

    });

    return EventWidget;
});
