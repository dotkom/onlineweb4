define(['handlebars', 'underscore', 'moment'], function(Handlebars, _, moment) {
    'use strict';
    // Date formatting using the moment library
    function dateFormat(context, block) {
        if (moment && context) {
            var f = _.isString(block) ? block : 'LLLL';
            return moment(context).format(f);
        } else {
            // Moment plugin not available. Return data as is.
            return context;
        }
    }
    Handlebars.registerHelper('dateFormat', dateFormat);
    return dateFormat;
});
