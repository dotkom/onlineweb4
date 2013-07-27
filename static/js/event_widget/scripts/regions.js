define(function(require) {
    var Marionette = require('backbone.marionette');

    return {
        main: new Marionette.Region({el: '#widget'})
    };
});
