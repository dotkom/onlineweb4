define(function(require) {
    'use strict';

    var Marionette = require('backbone.marionette');
    var eventItemTemplate = require('hbs!templates/event_item.tpl');
    var emptyTemplate = require('hbs!templates/empty.tpl');

    var EventItemView = Marionette.ItemView.extend({
        template: eventItemTemplate,
        className: 'event span4'
    });

    var Widget = Marionette.CollectionView.extend({
        itemView: EventItemView,
        emptyView: Marionette.ItemView.extend({
            template: emptyTemplate
        })
    });

    return Widget;
});
