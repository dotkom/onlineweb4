export const toggleEventTypeDisplay = (state, eventType) => (
  Object.assign({}, state.eventTypes, {
    [eventType.id]: Object.assign({}, eventType, {
      display: !eventType.display,
    }),
  })
);

export const setEventsForEventTypeId = (state, eventTypeId, events) => (
  Object.assign({}, state.eventTypes, {
    [eventTypeId]: Object.assign({}, state.eventTypes[eventTypeId], {
      events,
    }),
  })
);
