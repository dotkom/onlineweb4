from apps.events.models import Event, TYPE_CHOICES

def get_group_restricted_events(user, all_events=False):
    """ Returns a queryset of events with attendance_event that a user has access to """
    types_allowed = get_types_allowed(user)

    if all_events:
        return Event.objects.filter(event_type__in=types_allowed)
    else:
        return Event.objects.filter(attendance_event__isnull=False, event_type__in=types_allowed)

def get_types_allowed(user):
    types_allowed = []

    groups = user.groups.all()

    if reduce(lambda r, g: g.name in ['Hovedstyret', 'dotKom'] or r, groups, False):
        return [t[0] for t in TYPE_CHOICES]

    for group in groups:
        if group.name == 'arrKom':
            types_allowed.append(1) # sosialt 
            types_allowed.append(4) # utflukt

        if group.name == 'bedKom':
            types_allowed.append(2) # bedriftspresentasjon 

        if group.name == 'fagKom':
            types_allowed.append(3) # kurs
    
    return types_allowed
