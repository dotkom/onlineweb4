# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _


User = settings.AUTH_USER_MODEL

DURATION = 30
# summer starts 1st June, ends 15th August
SUMMER = ((6, 1), (8, 15))
# winter starts 1st December, ends 15th January
WINTER = ((12, 1), (1, 15))


def get_expiration_date(user):
    if user:
        marks = MarkUser.objects.filter(user=user).order_by('-expiration_date')
        if marks:
            return marks[0].expiration_date
    return None


class MarksManager(models.Manager):

    @staticmethod
    def all_active():
        return Mark.objects.filter(given_to__expiration_date__gt=timezone.now().date())

    @staticmethod
    def active(user):
        return MarkUser.objects.filter(user=user).filter(expiration_date__gt=timezone.now().date())

    @staticmethod
    def inactive(user=None):
        return MarkUser.objects.filter(user=user).filter(expiration_date__lte=timezone.now().date())


class Mark(models.Model):
    CATEGORY_CHOICES = (
        (0, _(u"Ingen")),
        (1, _(u"Sosialt")),
        (2, _(u"Bedriftspresentasjon")),
        (3, _(u"Kurs")),
        (4, _(u"Tilbakemelding")),
        (5, _(u"Kontoret")),
        (6, _(u"Betaling")),
    )

    title = models.CharField(_(u"tittel"), max_length=155)
    added_date = models.DateField(_(u"utdelt dato"))
    given_by = models.ForeignKey(
        User,
        related_name="mark_given_by",
        verbose_name=_(u"gitt av"),
        editable=False,
        null=True,
        blank=True
    )
    last_changed_date = models.DateTimeField(_(u"sist redigert"), auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(
        User,
        related_name="marks_last_changed_by",
        verbose_name=_(u"sist redigert av"),
        editable=False,
        null=True,
        blank=False
    )
    description = models.CharField(
        _(u"beskrivelse"),
        max_length=255,
        help_text=_(
            u"Hvis dette feltet etterlates blankt vil det fylles med en standard grunn for typen prikk som er valgt."
        ),
        blank=True
    )
    category = models.SmallIntegerField(_(u"kategori"), choices=CATEGORY_CHOICES, default=0)

    # managers
    objects = models.Manager()  # default manager
    marks = MarksManager()  # active marks manager

    def __unicode__(self):
        return _(u"Prikk for %s") % self.title

    def save(self, *args, **kwargs):
        if not self.added_date:
            self.added_date = timezone.now().date()
        super(Mark, self).save(*args, **kwargs)

    def delete(self, **kwargs):
        given_to = [mu.user for mu in self.given_to.all()]
        super(Mark, self).delete()
        for user in given_to:
            _fix_mark_history(user)

    class Meta(object):
        verbose_name = _(u"Prikk")
        verbose_name_plural = _(u"Prikker")
        permissions = (
            ('view_mark', 'View Mark'),
        )


class MarkUser(models.Model):
    """
    One entry for a user that has received a mark.
    """
    mark = models.ForeignKey(Mark, related_name="given_to")
    user = models.ForeignKey(User)

    expiration_date = models.DateField(_(u"utløpsdato"), editable=False)

    def save(self, *args, **kwargs):
        run_history_update = False
        if not self.expiration_date:
            self.expiration_date = timezone.now().date()
            run_history_update = True
        super(MarkUser, self).save(*args, **kwargs)
        if run_history_update:
            _fix_mark_history(self.user)

    def delete(self):
        super(MarkUser, self).delete()
        _fix_mark_history(self.user)

    def __unicode__(self):
        return _(u"Mark entry for user: %s") % self.user.get_full_name()

    class Meta:
        unique_together = ("user", "mark")
        ordering = ('expiration_date',)
        permissions = (
            ('view_userentry', 'View UserEntry'),
        )


def _fix_mark_history(user):
    """
    Goes through a users complete mark history and resets all expiration dates.

    The reasons for doing it this way is that the mark rules now insist on marks building
    on previous expiration dates if such exists. Instead of having the entire mark database
    be a linked list structure, it can be simplified to guarantee the integrity of the
    expiration dates by running this whenever;

     * new Mark is saved or deleted
     * a new MarkUser entry is made
     * an existing MarkUser entry is deleted
    """
    markusers = MarkUser.objects.filter(user=user).order_by('mark__added_date')
    last_expiry_date = None
    for entry in markusers:
        # If there's a last_expiry date, it means a mark has been processed already.
        # If that expiration date is within a DURATION of this added date, build on it.
        if last_expiry_date and entry.mark.added_date - timedelta(days=DURATION) < last_expiry_date:
            entry.expiration_date = _get_with_duration_and_vacation(last_expiry_date)
        # If there is no last_expiry_date or the last expiry date is over a DURATION old
        # we add DURATIION days from the added date of the mark.
        else:
            entry.expiration_date = _get_with_duration_and_vacation(entry.mark.added_date)
        entry.save()
        last_expiry_date = entry.expiration_date


def _get_with_duration_and_vacation(added_date=timezone.now()):
    """
    Checks whether the span of a marks duration needs to have vacation durations added.
    """

    if type(added_date) == datetime:
        added_date = added_date.date()

    # Add the duration
    expiry_date = added_date + timedelta(days=DURATION)
    # Set up the summer and winter vacations
    summer_start_date = date(added_date.year, SUMMER[0][0], SUMMER[0][1])
    summer_end_date = date(added_date.year, SUMMER[1][0], SUMMER[1][1])
    first_winter_start_date = date(added_date.year, WINTER[0][0], WINTER[0][1])
    first_winter_end_date = date(added_date.year + 1, WINTER[1][0], WINTER[1][1])
    second_winter_end_date = date(added_date.year, WINTER[1][0], WINTER[1][1])

    # If we're in the middle of summer, add the days remaining of summer
    if summer_start_date < added_date < summer_end_date:
        expiry_date += timedelta(days=(summer_end_date - added_date).days)
    # If the number of days between added_date and the beginning of summer vacation is less
    # than the duration, we need to add the length of summer to the expiry date
    elif 0 < (summer_start_date - added_date).days < DURATION:
        expiry_date += timedelta(days=(summer_end_date - summer_start_date).days)
    # Same for middle of winter vacation, which will be at the end of the year
    elif first_winter_start_date < added_date < first_winter_end_date:
        expiry_date += timedelta(days=(first_winter_end_date - added_date).days)
    # And for before the vacation
    elif 0 < (first_winter_start_date - added_date).days < DURATION:
        expiry_date += timedelta(days=(first_winter_end_date - first_winter_start_date).days)
    # Then we need to check the edge case where now is between newyears and and of winter vacation
    elif second_winter_end_date > added_date:
        expiry_date += timedelta(days=(second_winter_end_date - added_date).days)

    return expiry_date


class Suspension(models.Model):

    user = models.ForeignKey(User)
    title = models.CharField(_(u'tittel'), max_length=64)
    description = models.CharField(_(u"beskrivelse"), max_length=255)
    active = models.BooleanField(default=True)
    added_date = models.DateTimeField(auto_now=True, editable=False)
    expiration_date = models.DateField(_(u"utløpsdato"), null=True, blank=True)

    # Using id because foreign key to Payment caused circular dependencies
    payment_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return "Suspension: " + unicode(self.user)

    # TODO URL
