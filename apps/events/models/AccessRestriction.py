from datetime import datetime, timedelta

from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.authentication.constants import FieldOfStudyType

from .Attendance import AttendanceResult, StatusCode
from .Event import User


class Rule(models.Model):
    """
    Super class for a rule object
    """

    SUCCESS = StatusCode.SUCCESS_UNKNOWN
    NOT_SATISFIED = StatusCode.NOT_SATISFIED_UNKNOWN
    DELAYED_SIGNUP = StatusCode.DELAYED_SIGNUP_UNKNOWN

    offset = models.PositiveSmallIntegerField(
        _("utsettelse"), help_text=_("utsettelse oppgis i timer"), default=0
    )

    def satisfies_constraint(self, user: User) -> bool:
        return True

    def satisfied(self, user: User, registration_start: datetime) -> AttendanceResult:
        if self.satisfies_constraint(user):
            postponed_start = registration_start + timedelta(hours=self.offset)
            if postponed_start < timezone.now():
                return AttendanceResult(self.SUCCESS)
            elif self.offset == 0:
                return AttendanceResult(StatusCode.SIGNUP_NOT_OPENED_YET)
            else:
                return AttendanceResult(self.DELAYED_SIGNUP, postponed_start)
        return AttendanceResult(self.NOT_SATISFIED)

    def __str__(self):
        return "Rule"

    class Meta:
        permissions = (("view_rule", "View Rule"),)
        default_permissions = ("add", "change", "delete")
        ordering = ("id",)


class FieldOfStudyRule(Rule):
    SUCCESS = StatusCode.SUCCESS_FIELD_OF_STUDY
    DELAYED_SIGNUP = StatusCode.DELAYED_SIGNUP_FIELD_OF_STUDY
    NOT_SATISFIED = StatusCode.NOT_SATISFIED_FIELD_OF_STUDY

    field_of_study = models.SmallIntegerField(
        _("studieretning"), choices=FieldOfStudyType.choices
    )

    def satisfies_constraint(self, user: User) -> bool:
        return self.field_of_study == user.field_of_study

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer" if self.offset > 1 else "time")
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
    SUCCESS = StatusCode.SUCCESS_GRADE
    DELAYED_SIGNUP = StatusCode.DELAYED_SIGNUP_GRADE
    NOT_SATISFIED = StatusCode.NOT_SATISFIED_GRADE

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
    SUCCESS = StatusCode.SUCCESS_USER_GROUP
    DELAYED_SIGNUP = StatusCode.DELAYED_SIGNUP_USER_GROUP
    NOT_SATISFIED = StatusCode.NOT_SATISFIED_USER_GROUP

    group = models.ForeignKey(Group, blank=False, null=False, on_delete=models.CASCADE)

    def satisfies_constraint(self, user: User) -> bool:
        return self.group in user.groups.all()

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer" if self.offset > 1 else "time")
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
        rules: list[Rule] = []
        rules.extend(self.field_of_study_rules.all())
        rules.extend(self.grade_rules.all())
        rules.extend(self.user_group_rules.all())
        return rules

    @property
    def rule_strings(self):
        return [str(rule) for rule in self.get_all_rules()]

    def satisfied(
        self, user: User, registration_start: datetime
    ) -> list[AttendanceResult]:
        errors = []

        for rule in self.get_all_rules():
            response = rule.satisfied(user, registration_start)
            if response.status:
                return [response]
            else:
                errors.append(response)

        return errors

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
