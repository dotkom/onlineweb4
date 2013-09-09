define(function(require) {
    'use strict';

    var Marionette = require('backbone.marionette');
    var RegionManager = require('regions');
    var EventCollection = require('event.collection');
    var Widget = require('views/widget.layout');
    var Controller = require('controller');

    var WidgetController = new Controller({

        index: function() {
            var events = new EventCollection();
            var xhr = events.fetch();
            
            xhr.done(function() {
                var widget = new Widget({collection: events});
                RegionManager.main.show(widget);
            });

            xhr.fail(function() {
                // XXX: TODO: Handle failure
            });

        },

        filtered: function(eventType, limit, offset) {
            // XXX: This kind of coupling is pretty, pretty
            // awful. The client have no business knowing the
            // internals of our data model. An identifier
            // should suffice, yes?
            var eventTypes = {
                'sosialt': 1,
                'bedpres': 2,
                'kurs': 3,
                'utflukt': 4,
                'internt': 5,
                'annet': 6
            };

            // This makes the available options explicit for
            // clarity's sake. The Collection itself should have
            // sane defaults if instantiated withhout parameters.
            var events = new EventCollection({
                eventType: eventTypes[eventType],
                limit: limit,
                offset: offset
            });
            var xhr = events.fetch();

            xhr.done(function() {
                var widget = new Widget({collection: events});
                RegionManager.main.show(widget);
            });
        }
    });

    var WidgetRouter = Marionette.AppRouter.extend({
        controller: WidgetController,

        appRoutes: {
            '': 'index',
            // Replace with page number?
            ':eventType(/)(:limit)(/)(:offset)': 'filtered'
        }
    });

    return WidgetRouter;
});
