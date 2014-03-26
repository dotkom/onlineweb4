from apps.events.models import Event

def get_group_restricted_events(user):
	""" Returns a queryset of events with attendance_event that a user has access to """
	types_allowed = []

	groups = user.groups.all()

	if 'Hovedstyret' or 'dotKom' in groups:
		return Event.objects.filter(attendance_event__isnull=False)

	for group in groups:
		if group.name == 'arrKom':
			types_allowed.append(1)
			types_allowed.append(4)

		if group.name == 'bedKom':
			types_allowed.append(2)

		if group.name == 'fagKom':
			types_allowed.append(3)


	return Event.objects.filter(attendance_event__isnull=False, type__in=types_allowed)
