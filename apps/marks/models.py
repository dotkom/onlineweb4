#-*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User

import reversion

class ActiveMarksManager(models.Manager):
    def get_queryset(self):
        return super(ActiveMarksManager, self).get_queryset().filter(expiration_date__gt=timezone.now())


class InactiveMarksManager(models.Manager):
    def get_queryset(self):
        return super(InactiveMarksManager, self).get_queryset().filter(expiration_date__lte=timezone.now())


class Mark(models.Model):
    CATEGORY_CHOICES = (
        (0, _(u"Ingen")),
        (1, _(u"Sosialt")),
        (2, _(u"Bedriftspresentasjon")),
        (3, _(u"Kurs")),
        (4, _(u"Tilbakemelding")),
        (5, _(u"Kontoret")),
    )

    title = models.CharField(_(u"tittel"), max_length=155)
    given_to = models.ManyToManyField(User, null=True, blank=True, through="UserEntry", verbose_name=_(u"gitt til"))
    added_date = models.DateField(_(u"utdelt dato"))
    expiration_date = models.DateField(_(u"utløpsdato"), editable=False)
    given_by = models.ForeignKey(User, related_name="mark_given_by", verbose_name=_(u"gitt av"), editable=False, null=True, blank=True)
    last_changed_date = models.DateTimeField(_(u"sist redigert"), auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(User, related_name="marks_last_changed_by",
        verbose_name=_(u"sist redigert av"), editable=False, null=True, blank=False)
    description = models.CharField(_(u"beskrivelse"), max_length=255,
                                   help_text=_(u"Hvis dette feltet etterlates blankt vil det fylles med "
                                               "en standard grunn for typen prikk som er valgt."),
                                   blank=True)
    category = models.SmallIntegerField(_(u"kategori"), choices=CATEGORY_CHOICES, default=0)

    # managers
    objects = models.Manager()  # default manager
    active = ActiveMarksManager()  # active marks manager
    inactive = InactiveMarksManager()  #inactive marks manager

    @property
    def is_active(self):
        return self.expiration_date > timezone.now()

    def __unicode__(self):
        return _(u"Prikk for %s") % self.title

    def save(self, *args, **kwargs):
        if not self.added_date:
            self.added_date = timezone.now()
        self.expiration_date = _get_expiration_date(self.added_date) 
        super(Mark, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u"Prikk")
        verbose_name_plural = _(u"Prikker")


reversion.register(Mark)


class UserEntry(models.Model):
    user = models.ForeignKey(User)
    mark = models.ForeignKey(Mark)

    def __unicode__(self):
        return _(u"UserEntry for %s") % self.user.get_full_name()

    class Meta:
        unique_together = ("user", "mark")


reversion.register(UserEntry)


def _get_expiration_date(added_date=timezone.now()):
    """
    Calculates the datetime in the future when a mark will expire. 
    """

    if type(added_date) == datetime:
        added_date = added_date.date()

    DURATION = 60
    # summer starts 1st June, ends 15th August
    SUMMER = ((6, 1), (8, 15))
    # winter starts 1st December, ends 15th January
    WINTER = ((12, 1), (1, 15))

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

    # The returned value is a timezone aware datetime object
    return timezone.make_aware(datetime.combine(expiry_date, time()), timezone.get_current_timezone())
