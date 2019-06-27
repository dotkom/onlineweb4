class GroupType:
    COMMITTEE = 'committee'
    NODE_COMMITTEE = 'node_committee'
    HOBBY_GROUP = 'hobby_group'
    OTHER = 'other'

    ALL_TYPES = (COMMITTEE, NODE_COMMITTEE, HOBBY_GROUP, OTHER)
    ALL_CHOICES = (
        (COMMITTEE, 'Komité'),
        (NODE_COMMITTEE, 'Nodekomité'),
        (HOBBY_GROUP, 'Interessegruppe'),
        (OTHER, 'Annet'),
    )


class RoleType:
    LEADER = 'leader'
    DEPUTY_LEADER = 'deputy_leader'
    TREASURER = 'treasurer'
    MEMBER = 'member'
    RETIRED = 'retired'
    ON_LEAVE = 'on_leave'
    CHIEF_EDITOR = 'chief_editor'

    ACTIVE_MEMBERS = (LEADER, DEPUTY_LEADER, TREASURER, MEMBER, CHIEF_EDITOR)

    ALL_TYPES = (LEADER, DEPUTY_LEADER, TREASURER, MEMBER, RETIRED, ON_LEAVE, CHIEF_EDITOR)
    ALL_CHOICES = (
        (LEADER, 'Leder'),
        (DEPUTY_LEADER, 'Nestleder'),
        (TREASURER, 'Økonomiansvarlig'),
        (MEMBER, 'Medlem'),
        (RETIRED, 'Pensjonert'),
        (ON_LEAVE, 'Permittert'),
        (CHIEF_EDITOR, 'Redaktør'),
    )
