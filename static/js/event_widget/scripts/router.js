define(function(require) {
    var Marionette = require('backbone.marionette');
    var EventCollection = require('event.collection');
    var Widget = require('widget.view');
    var RegionManager = require('regions');

    var WidgetController = {
        index: function() {
            var events = new EventCollection();
            events.fetch().done(function() {
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
