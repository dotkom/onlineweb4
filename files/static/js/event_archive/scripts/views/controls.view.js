define(function(require) {
    'use strict';

    var Marionette = require('backbone.marionette');
    var controlsTemplate = require('hbs!templates/controls.tpl');

    var Controls = Marionette.ItemView.extend({
        template: controlsTemplate
    });

    return Controls;
});
