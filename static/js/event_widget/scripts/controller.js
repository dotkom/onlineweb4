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

    /*
     * Converts a queryString such as '?event_type=1&author=foo' to
     * object {event_type: 1, author: foo}
     */

    Controller.prototype.extractParams = function(queryString) {
        var params = {};
        if (queryString) {
            _.each(
                _.map(decodeURI(queryString).split(/&/g), function(el){
                    var aux = el.split('='), o = {};
                    if (aux.length >= 1){
                        var val;
                        if (aux.length === 2) {
                            val = aux[1];
                        }
                        o[aux[0]] = val;
                    }
                    return o;
                }),
                function(o){
                    _.extend(params,o);
                }
            );
        }
        return params;
    };

    return Controller;
});
