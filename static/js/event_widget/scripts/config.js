require.config({
    baseUrl: '/static/js/event_widget/scripts/',
    paths: {
        'almond': '../bower_components/almond/almond',
        'backbone': '../bower_components/backbone-amd/backbone',
        'backbone.wreqr': '../bower_components/backbone.wreqr/lib/amd/backbone.wreqr',
        'backbone.babysitter': '../bower_components/backbone.babysitter/lib/amd/backbone.babysitter',
        'backbone.tastypie': 'vendor/backbone-tastypie',
        'underscore': '../bower_components/underscore-amd/underscore',
        'jquery': '../bower_components/jquery/jquery',
        'handlebars': '../bower_components/hbs/handlebars',
        'hbs': '../bower_components/hbs/hbs',
        'json2': '../bower_components/hbs/hbs/json2',
        'i18nprecompile': '../bower_components/hbs/hbs/i18nprecompile',

        'templates': '../templates'
    },

    hbs: {
        disableI18n: true,
        helperPathCallback: function(name) {
            "use strict";
            return '../templates/helpers/' + name;
        }
    },

    shim: {
        'underscore': {exports: '_'},

        'backbone': {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },

        'backbone.stickit': {
            deps: ['backbone'],
            exports: 'Backbone'
        },

        'hbs': {
            deps: ['handlebars']
        }
    }
});

require(['main'], function(Main) {
    new Main();
});
