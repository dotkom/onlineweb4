from django.utils.translation import ugettext as _


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

    # Members in these roles are counted as active members of a group
    ACTIVE_MEMBERS = (LEADER, DEPUTY_LEADER, TREASURER, MEMBER, CHIEF_EDITOR)
    # A group can only have a single member with these roles each
    SINGLUAR_POSITIONS = (LEADER, DEPUTY_LEADER, TREASURER, CHIEF_EDITOR)

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


class FieldOfStudyType:
    GUEST = 0
    BACHELOR = 1
    # master degrees take up the interval [10,30]
    SOFTWARE_ENGINEERING = 10
    DATABASE_AND_SEARCH = 11
    ALGORITHMS = 12
    GAME_TECHNOLOGY = 13
    ARTIFICIAL_INTELLIGENCE = 14
    HEALTH_INFORMATICS = 15
    INTERACTION_DESIGN = 16
    OTHER_MASTERS = 30

    SOCIAL_MEMBER = 40
    PHD = 80
    INTERNATIONAL = 90
    OTHER_MEMBER = 100

    ALL_MASTERS = (
        SOFTWARE_ENGINEERING,
        DATABASE_AND_SEARCH,
        ALGORITHMS,
        GAME_TECHNOLOGY,
        ARTIFICIAL_INTELLIGENCE,
        HEALTH_INFORMATICS,
        INTERACTION_DESIGN,
        OTHER_MASTERS,
    )

    ALL_CHOICES = [
        (GUEST, _('Gjest')),
        (BACHELOR, _('Bachelor i Informatikk')),
        (SOFTWARE_ENGINEERING, _('Programvaresystemer')),
        (DATABASE_AND_SEARCH, _('Databaser og søk')),
        (ALGORITHMS, _('Algoritmer og datamaskiner')),
        (GAME_TECHNOLOGY, _('Spillteknologi')),
        (ARTIFICIAL_INTELLIGENCE, _('Kunstig intelligens')),
        (HEALTH_INFORMATICS, _('Helseinformatikk')),
        (INTERACTION_DESIGN, _('Interaksjonsdesign, spill- og læringsteknologi')),
        (OTHER_MASTERS, _('Annen mastergrad')),
        (SOCIAL_MEMBER, _('Sosialt medlem')),
        (PHD, _('PhD')),
        (INTERNATIONAL, _('International')),
        (OTHER_MEMBER, _('Annet Onlinemedlem')),
    ]
    ALL_TYPES = [t for t, _ in ALL_CHOICES]
