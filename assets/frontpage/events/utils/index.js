export const toggleEventTypeDisplay = (state, eventType) => {
  const newState = Object.assign({}, state);
  const selected = [];
  let eventCount = 0;

  for (const type of Object.values(newState.eventTypes)) {
    eventCount++;
    if (type.display) {
      selected.push(type.id);
    }
  }

  // If only one event is selected and is being deselected, then show all and set dirty to false
  if (selected.length === 1 && eventType.id === selected[0]) {
    state.dirty = false;
    for (const type of Object.values(newState.eventTypes)) {
      Object.assign(type, {
        display: true,
      });
    }
  }

  // If only one event is unselected and is being selected, then show all and set dirty to true
  else if (selected.length === eventCount - 1 && selected.indexOf(eventType.id) === -1) {
    state.dirty = true;
    for (const type of Object.values(newState.eventTypes)) {
      Object.assign(type, {
        display: true,
      });
    }
  }

  // If all events are selected and dirty is false, then deselect the all other than the selected and set dirty to true
  else if (selected.length === eventCount && !state.dirty) {
    state.dirty = true;
    for (const type of Object.values(newState.eventTypes)) {
      if (type.id !== eventType.id) {
        Object.assign(type, {
          display: false,
        });
      }
    }
  }

  // If none of the edge cases above, then toggle as usual
  else {
    state.dirty = true;
    Object.assign(newState.eventTypes, {
      [eventType.id]: Object.assign({}, eventType, {
        display: !eventType.display,
      }),
    });
  }

  return Object.assign({}, state.eventTypes, newState.eventTypes);
}

export const setEventsForEventTypeId = (state, eventTypeId, events) => (
  Object.assign({}, state.eventTypes, {
    [eventTypeId]: Object.assign({}, state.eventTypes[eventTypeId], {
      events,
      loaded: true,
    }),
  })
);
