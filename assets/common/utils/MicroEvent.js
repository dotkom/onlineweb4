/**
 * Created by myth on 3/10/16.
 */

const MicroEvent = () => {
  const debug = window.DEBUG;
  const events = {};

  return {
    /**
     * Fire an event of type "event" to all registered listeners for that type.
     * @param {string} event The event type to be triggered
     * @param {*} [payload] An optional event payload
     */
    fire(event, payload) {
      if (debug) console.log(`Firing event: ${event}`, 'Payload: ', payload);

      // Attempt to fetch the event queue and fire event to all listeners
      const listeners = events[event];
      if (typeof listeners === 'undefined') return;
      for (let i = 0; i < listeners.length; i += 1) listeners[i](event, payload);
    },

    /**
     * Register a callback on a given event type, that will invoke the
     * callback function once the event fires.
     * @param {string} event Event type
     * @param {function} callback Callback function accepting
     * two arguments: {string} event, {*} payload
     */
    on(event, callback) {
      if (debug) console.log(`Registering callback on event: ${event}`);

      if (typeof events[event] === 'undefined') {
        events[event] = [];
      }
      events[event].push(callback);
    },
  };
};

export default MicroEvent;
