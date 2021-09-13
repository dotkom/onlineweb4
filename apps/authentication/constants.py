from django.utils.translation import gettext as _
from django.db import models


class GroupType(models.TextChoices):
    COMMITTEE = "committee", _("Komité")
    NODE_COMMITTEE = "node_committee", _("Nodekomité")
    HOBBY_GROUP = "hobby_group", _("Interessegruppe")
    OTHER = "other", _("Annet")


class RoleType(models.TextChoices):
    LEADER = "leader", _("Leder")
    BOARD_MEMBER = "board_member", _("Styremedlem")
    DEPUTY_LEADER = "deputy_leader", _("Nestleder")
    TREASURER = "treasurer", _("Økonomiansvarlig")
    CHIEF_EDITOR = "chief_editor", _("Redaktør")


class FieldOfStudyType(models.IntegerChoices):
    GUEST = 0, _("Gjest")
    BACHELOR = 1, _("Bachelor i Informatikk")

    @classmethod
    def ALL_MASTERS(cls):
        # master degrees take up the interval [10,30]
        return [choice for choice in cls.values if 10 <= choice <= 30]

    SOFTWARE_ENGINEERING = 10, _("Programvaresystemer")
    DATABASE_AND_SEARCH = 11, _("Databaser og søk")
    ALGORITHMS = 12, _("Algoritmer og datamaskiner")
    GAME_TECHNOLOGY = 13, _("Spillteknologi")
    ARTIFICIAL_INTELLIGENCE = 14, _("Kunstig intelligens")
    HEALTH_INFORMATICS = 15, _("Helseinformatikk")
    INTERACTION_DESIGN = 16, _("Interaksjonsdesign, spill- og læringsteknologi")
    OTHER_MASTERS = 30, _("Annen mastergrad")

    SOCIAL_MEMBER = 40, _("Sosialt medlem")
    PHD = 80, _("PhD")
    INTERNATIONAL = 90, _("International")
    OTHER_MEMBER = 100, _("Annet Onlinemedlem")
