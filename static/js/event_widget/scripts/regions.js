define(function(require) {
    'use strict';

    var Marionette = require('backbone.marionette');

    return {
        main: new Marionette.Region({el: '#widget'})
    };
});
