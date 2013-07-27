define(function(require) {
    var Marionette = require('backbone.marionette');
    var EventCollection = require('event.collection');
    var Widget = require('widget.view');
    var RegionManager = require('regions');

    var WidgetController = {
        index: function() {
            console.log('In your controller, WOAH');
            var events = new EventCollection();
            events.fetch().done(function() {
                console.log(events);    
                var widget = new Widget({collection: events});
                RegionManager.main.show(widget);
            });

        }
    };

    var WidgetRouter = Marionette.AppRouter.extend({
        controller: WidgetController,
        appRoutes: {
            '': 'index'
        }
    });

    return WidgetRouter;
});
