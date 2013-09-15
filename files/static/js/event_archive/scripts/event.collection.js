define(function(require) {
    'use strict';

    var $ = require('jquery');
    var Backbone = require('backbone');
    var EventModel = Backbone.Model.extend({});

    var EventCollection = Backbone.Collection.extend({
        model: EventModel,

        initialize: function(options) {
            options = options || {};
            this.limit = options.limit || 20;
            this.offset = options.offset || 0;
            this.eventType = options.eventType || null;
        },

        url: function() {
            return '/api/v0/events?' + this.params();
        },

        parse: function(response) {
            // XXX: The default behaviour of Tastypie APIs are
            // to return the desired objects on the 'objects'-key.
            // However, we return { events: [...]} instead.
            // If we decide to structure more than this widget
            // using Backbone it may be wise to rethink that
            // approach. The default behaviour would allow us to
            // create a base model with a working parse step
            // out of the box.
            return response.events || response;
        },

        // Parameterizes the desired options passed to the collection.
        // A more general solution is struggling to break free here,
        // I think.
        params: function() {
            var p = {limit: this.limit, offset: this.offset};
            if (this.eventType) {p.event_type = this.eventType;}
            return $.param(p);
        }

    });

    return EventCollection;
});
