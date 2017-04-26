export const toggleEventTypeDisplay = (state, eventType) => {
  let newState = state;
  let eventCount = 0;
  let selected = [];
  for (let key in state.eventTypes) {
    eventCount++;
    if (state.eventTypes[key].display) {
      selected.push(key);
    }
  }

  // If only one event is selected and is being deselected, then show all and set dirty to false
  if (selected.length === 1 && eventType === newState.eventTypes[selected[0]]) {
    newState.dirty = false;
    for (let key in state.eventTypes) {
      newState.eventTypes[key] = Object.assign({}, newState.eventTypes[key], {
        display: true,
      })
    }
  }

  // If only one event is unselected and is being selected, then show all and set dirty to true
  else if (selected.length === eventCount - 1 && selected.indexOf(eventType.id) === -1) {
    newState.dirty = true;
    for (let key in state.eventTypes) {
      newState.eventTypes[key] = Object.assign({}, newState.eventTypes[key], {
        display: true,
      })
    }
  }

  // If all events are selected and dirty is false, then deselect the all other than the selected and set dirty to true
  else if (selected.length === eventCount && !state.dirty) {
    newState.dirty = true;
    for (let key in state.eventTypes) {
      if (key !== eventType.id) {
        newState.eventTypes[key] = Object.assign({}, newState.eventTypes[key], {
          display: false,
        })
      }
    }
  }

  // If all events are selected and dirty is true, then deselect the selected one and leave dirty as true
  else if (selected.length === eventCount && state.dirty) {
    newState.eventTypes = Object.assign({}, state.eventTypes, {
      [eventType.id]: Object.assign({}, eventType, {
        display: !eventType.display,
      }),
    });
  }

  // If none of the edge cases above
  else {
    newState.eventTypes = Object.assign({}, state.eventTypes, {
      [eventType.id]: Object.assign({}, eventType, {
        display: !eventType.display,
      }),
    });
  }

  return Object.assign({}, state.eventTypes, newState.eventTypes);
};

export const setEventsForEventTypeId = (state, eventTypeId, events) => (
  Object.assign({}, state.eventTypes, {
    [eventTypeId]: Object.assign({}, state.eventTypes[eventTypeId], {
      events,
      loaded: true,
    }),
  })
);
