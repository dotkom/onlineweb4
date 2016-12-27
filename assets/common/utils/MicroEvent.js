/**
 * Created by myth on 3/10/16.
 */

var MicroEvent = function () {
  var debug = window.DEBUG
  var self = this
  self.events = {}

  return {
    /**
     * Fire an event of type "event" to all registered listeners for that type.
     * @param {string} event The event type to be triggered
     * @param {*} [payload] An optional event payload
     */
    fire: function (event, payload) {
      if (debug) console.log('Firing event: ' + event, 'Payload: ', payload)

      // Attempt to fetch the event queue and fire event to all listeners
      var listeners = self.events[event]
      if (typeof listeners === 'undefined') return
      for (var i = 0; i < listeners.length; i++) listeners[i](event, payload)
    },

    /**
     * Register a callback on a given event type, that will invoke the callback function once the event fires.
     * @param {string} event Event type
     * @param {function} callback Callback function accepting two arguments: {string} event, {*} payload
     */
    on: function (event, callback) {
      if (debug) console.log('Registering callback on event: ' + event)

      if (typeof self.events[event] === 'undefined') {
        self.events[event] = []
      }
      self.events[event].push(callback)
    }
  }
}

export default MicroEvent;
