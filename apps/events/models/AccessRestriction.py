from datetime import datetime, timedelta
from typing import List

from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.authentication.constants import FieldOfStudyType

from .Event import User


class Rule(models.Model):
    """
    Super class for a rule object
    """

    success_code = 213
    not_opened_code = 402
    delayed_signup_code = 423
    delayed_singup_message = _("Du har utsatt påmelding")
    not_satisfied_code = 413
    not_satisfied_message = _("Du har ikke tilgang til å melde deg på arrangementet")

    offset = models.PositiveSmallIntegerField(
        _("utsettelse"), help_text=_("utsettelse oppgis i timer"), default=0
    )

    def get_offset_time(self, time: timezone.datetime):
        if type(time) is not datetime:
            raise TypeError("time must be a datetime, not %s" % type(time))
        else:
            return time + timedelta(hours=self.offset)

    def satisfies_constraint(self, user: User) -> bool:
        return True

    def satisfied(self, user: User, registration_start: timezone.datetime):
        """Override method"""

        if self.satisfies_constraint(user):
            offset_datetime = self.get_offset_time(registration_start)
            # If the offset is in the past, it means you can attend even with the offset
            if offset_datetime < timezone.now():
                return {
                    "status": True,
                    "message": None,
                    "status_code": self.success_code,
                }
            # If there is no offset, the signup just hasn't started yet
            elif self.offset == 0:
                return {
                    "status": False,
                    "message": _("Påmeldingen har ikke åpnet enda."),
                    "status_code": self.not_opened_code,
                }
            # In the last case there is a delayed signup
            else:
                return {
                    "status": False,
                    "message": self.delayed_singup_message,
                    "offset": offset_datetime,
                    "status_code": self.delayed_signup_code,
                }
        return {
            "status": False,
            "message": self.not_satisfied_message,
            "status_code": self.not_satisfied_code,
        }

    def __str__(self):
        return "Rule"

    class Meta:
        permissions = (("view_rule", "View Rule"),)
        default_permissions = ("add", "change", "delete")
        ordering = ("id",)


class FieldOfStudyRule(Rule):
    success_code = 210
    delayed_signup_code = 420
    delayed_singup_message = _("Din studieretning har utsatt påmelding.")
    not_satisfied_code = 410
    not_satisfied_message = _(
        "Din studieretning er en annen enn de som har tilgang til dette arrangementet."
    )

    field_of_study = models.SmallIntegerField(
        _("studieretning"), choices=FieldOfStudyType.ALL_CHOICES
    )

    def satisfies_constraint(self, user: User) -> bool:
        return self.field_of_study == user.field_of_study

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer") if self.offset > 1 else _("time")
            return _("%s etter %d %s") % (
                str(self.get_field_of_study_display()),
                self.offset,
                time_unit,
            )
        return str(self.get_field_of_study_display())

    class Meta:
        permissions = (("view_fieldofstudyrule", "View FieldOfStudyRule"),)
        default_permissions = ("add", "change", "delete")


class GradeRule(Rule):
    success_code = 211
    delayed_signup_code = 421
    delayed_singup_message = _("Ditt klassetrinn har utsatt påmelding.")
    not_satisfied_code = 411
    not_satisfied_message = _(
        "Ditt klassetrinn har ikke tilgang til dette arrangementet.."
    )

    grade = models.SmallIntegerField(_("klassetrinn"), null=False)

    def satisfies_constraint(self, user: User) -> bool:
        return self.grade == user.year

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer") if self.offset > 1 else _("time")
            return _("%s. klasse etter %d %s") % (self.grade, self.offset, time_unit)
        return _("%s. klasse") % self.grade

    class Meta:
        permissions = (("view_graderule", "View GradeRule"),)
        default_permissions = ("add", "change", "delete")


class UserGroupRule(Rule):
    success_code = 212
    delayed_signup_code = 422
    delayed_singup_message = _("Brukergruppene dine har utsatt påmelding")
    not_satisfied_code = 412
    not_satisfied_message = _(
        "Din brukergruppe har ikke tilgang til dette arrangementet."
    )

    group = models.ForeignKey(Group, blank=False, null=False, on_delete=models.CASCADE)

    def satisfies_constraint(self, user: User) -> bool:
        return self.group in user.groups.all()

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer") if self.offset > 1 else _("time")
            return _("%s etter %d %s") % (str(self.group), self.offset, time_unit)
        return str(self.group)

    class Meta:
        permissions = (("view_usergrouprule", "View UserGroupRule"),)
        default_permissions = ("add", "change", "delete")


class RuleBundle(models.Model):
    """
    Access restriction rule object
    """

    description = models.CharField(
        _("beskrivelse"), max_length=100, blank=True, null=True
    )
    field_of_study_rules = models.ManyToManyField(FieldOfStudyRule, blank=True)
    grade_rules = models.ManyToManyField(GradeRule, blank=True)
    user_group_rules = models.ManyToManyField(UserGroupRule, blank=True)

    def get_all_rules(self):
        rules: List[Rule] = []
        rules.extend(self.field_of_study_rules.all())
        rules.extend(self.grade_rules.all())
        rules.extend(self.user_group_rules.all())
        return rules

    @property
    def rule_strings(self):
        return [str(rule) for rule in self.get_all_rules()]

    def satisfied(self, user, registration_start):

        errors = []

        for rule in self.get_all_rules():
            response = rule.satisfied(user, registration_start)
            if response["status"]:
                return [response]
            else:
                errors.append(response)

        return errors

    def get_minimum_offset_for_user(self, user: User):
        offsets = [
            rule.offset
            for rule in self.get_all_rules()
            if rule.satisfies_constraint(user)
        ]
        if len(offsets) == 0:
            return timezone.timedelta(hours=0)
        offsets.sort()
        return timezone.timedelta(hours=offsets[0])

    def __str__(self):
        if self.description:
            return self.description
        elif self.rule_strings:
            return ", ".join(self.rule_strings)
        else:
            return _("Tom rule bundle.")

    class Meta:
        permissions = (("view_rulebundle", "View RuleBundle"),)
        default_permissions = ("add", "change", "delete")
        ordering = ("id",)
