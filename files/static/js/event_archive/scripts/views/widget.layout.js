define(function(require) {
    'use strict';

    var Marionette = require('backbone.marionette');
    var EventCollectionView = require('views/events.view');
    var ControlsView = require('views/controls.view');
    var widgetLayoutTemplate = require('hbs!templates/widget.layout.tpl');

    var Widget = Marionette.Layout.extend({
        template: widgetLayoutTemplate,
        id: 'widget',

        regions: {
            controls: '[data-js-archive-controls]',
            content: '[data-js-event-list]'
        },

        onShow: function() {
            var widgetView = new EventCollectionView({collection: this.collection});
            this.content.show(widgetView);

            var controlsView = new ControlsView();
            this.controls.show(controlsView);
        }
    });

    return Widget;
});
