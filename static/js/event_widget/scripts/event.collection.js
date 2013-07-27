define(function(require) {
    'use strict';

    var Backbone = require('backbone');

    var EventModel = Backbone.Model.extend({});

    var EventCollection = Backbone.Collection.extend({
        model: EventModel,

        url: '/api/v0/events?format=json',
        parse: function(response) {
            return response.events || response;
        }

    });

    return EventCollection;
});
