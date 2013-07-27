define(function(require) {
    var Marionette = require('backbone.marionette');
    var eventItemTemplate = require('hbs!templates/event_item.tpl');

    var EventItemView = Marionette.ItemView.extend({
        template: eventItemTemplate
    });

    var Widget = Marionette.CollectionView.extend({
        initialize: function(options) {
            console.log("widget opts", options);
        },

        itemView: EventItemView
    });

    return Widget;
});
