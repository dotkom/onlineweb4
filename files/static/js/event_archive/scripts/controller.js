define(function(require) {
    'use strict';

    var _ = require('underscore');

    var Controller = function(obj) {
        obj = obj || {};

        for (var key in obj) {
            if (key === 'initialize') { continue; }
            this.add(key, obj[key]);
        }

        if (obj.initialize) { obj.initialize.apply(this, arguments); }
        return this;
    };

    /*
     * Adds a method to the controller. For example:
     * .add('index', function(someId) { ... });
     */

    Controller.prototype.add = function(name, method) {
        if (!_.isString(name)) { return; }
        if (!_.isFunction(method)) { return; }
        this[name] = method;
    };

    return Controller;
});
