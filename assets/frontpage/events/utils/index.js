export const toggleEventTypeDisplay = (state, eventType) => {
  const newState = Object.assign({}, state);
  const selected = [];
  let eventCount = 0;

  Object.values(newState.eventTypes).forEach((type) => {
    eventCount += 1;
    if (type.display) {
      selected.push(type.id);
    }
  });

  if (selected.length === 1 && eventType.id === selected[0]) {
    // If only one event is selected and is being deselected,
    // then show all and set dirty to false
    Object.assign(state, { dirty: false });

    Object.values(newState.eventTypes).forEach((type) => {
      Object.assign(type, {
        display: true,
      });
    });
  } else if (selected.length === eventCount - 1 && selected.indexOf(eventType.id) === -1) {
    // If only one event is unselected and is being selected,
    // then show all and set dirty to true
    Object.assign(state, { dirty: true });

    Object.values(newState.eventTypes).forEach((type) => {
      Object.assign(type, {
        display: true,
      });
    });
  } else if (selected.length === eventCount && !state.dirty) {
    // If all events are selected and dirty is false,
    // then deselect the all other than the selected and set dirty to true
    Object.assign(state, { dirty: true });

    Object.values(newState.eventTypes)
      .filter(type => type.id !== eventType.id)
      .forEach((type) => {
        Object.assign(type, {
          display: false,
        });
      });
  } else {
    // If none of the edge cases above, then toggle as usual
    Object.assign(newState.eventTypes, {
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
