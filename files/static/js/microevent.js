/**
 * Created by myth on 3/10/16.
 */

var MicroEvent = function () {

    var debug = true;
    var self = this
    self.events = {}

    return {
        // Fire an event
        fire: function (event) {

            if (debug) console.log('Firing event: ' + event)

            // Attempt to fetch the event queue and fire event to all listeners
            var listeners = self.events[event]
            if (typeof listeners === 'undefined') return
            for (var i = 0; i < listeners.length; i++) listeners[i]()
        },

        // Register as an event listener
        on: function (event, callback) {

            if (debug) console.log('Registering callback on event: ' + event)

            if (typeof self.events[event] === 'undefined') {
                self.events[event] = []
            }
            self.events[event].push(callback)
        }
    }
}


