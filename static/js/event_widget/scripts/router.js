define(function(require) {
    'use strict';

    var Marionette = require('backbone.marionette');
    var RegionManager = require('regions');
    var EventCollection = require('event.collection');
    var Widget = require('views/widget.layout');
    var Controller = require('controller');

    var WidgetController = new Controller({
        index: function(queryString) {
            var params = this.extractParams(queryString);

            var events = new EventCollection();
            var xhr = events.fetch({ data: params });
            
            xhr.done(function() {
                var widget = new Widget({collection: events});
                RegionManager.main.show(widget);
            });

            xhr.fail(function() {
                // XXX: TODO: Handle failure
            });

        }
    });

    var WidgetRouter = Marionette.AppRouter.extend({
        controller: WidgetController,
        appRoutes: {
            '(/)?:queryString': 'index'
        }
    });

    return WidgetRouter;
});
