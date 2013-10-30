#-*- coding: utf-8 -*-

import datetime
from django.utils import timezone

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User

class ActiveMarksManager(models.Manager):
    def get_query_set(self):
        threshhold = get_threshold()

        return super(ActiveMarksManager, self).get_query_set().filter(mark_added_date__gt=threshhold)


class InactiveMarksManager(models.Manager):
    def get_query_set(self):
        threshhold = get_threshold()

        return super(InactiveMarksManager, self).get_query_set().filter(mark_added_date__lte=threshhold)


class Mark(models.Model):
    CATEGORY_CHOICES = (
        (0, _(u"Ingen")),
        (1, _(u"Sosialt")),
        (2, _(u"Bedriftspresentasjon")),
        (3, _(u"Kurs")),
        (4, _(u"Tilbakemelding")),
        (5, _(u"Kontoret")),
    )

    title = models.CharField(_(u"tittel"), max_length=50)
    given_to = models.ManyToManyField(User, null=True, blank=True, through="UserEntry", verbose_name=_(u"gitt til"))
    mark_added_date = models.DateTimeField(_(u"utdelt dato"), auto_now_add=True)
    given_by = models.ForeignKey(User, related_name="mark_given_by", verbose_name=_(u"gitt av"), editable=False, null=True, blank=True)
    last_changed_date = models.DateTimeField(_(u"sist redigert"), auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(User, related_name="marks_last_changed_by",
        verbose_name=_(u"sist redigert av"), editable=False, null=True, blank=False)
    description = models.CharField(_(u"beskrivelse"), max_length=100,
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
        return self.mark_added_date > get_threshold()

    def __unicode__(self):
        return _(u"Prikk for %s") % self.title

    class Meta:
        verbose_name = _(u"Prikk")
        verbose_name_plural = _(u"Prikker")


class UserEntry(models.Model):
    user = models.ForeignKey(User)
    mark = models.ForeignKey(Mark)

    def __unicode__(self):
        return _(u"UserEntry for %s") % self.user.get_full_name()

    class Meta:
        unique_together = ("user", "mark")


def get_threshold():
    DURATION = 60
    # summer starts 1st June, ends 15th August
    SUMMER = ((6, 1), (8, 15))
    # winter starts 1st December, ends 15th January
    WINTER = ((12, 1), (1, 15))

    # Todays date
    now = timezone.now().date()
    print "now = "+ str(now)
    # Threshhold is the day in the past which marks will be filtered on by mark_added_date
    threshold = now - datetime.timedelta(days=DURATION)
    summer_start_date = datetime.date(now.year, SUMMER[0][0], SUMMER[0][1])
    summer_end_date = datetime.date(now.year, SUMMER[1][0], SUMMER[1][1])
    first_winter_start_date = datetime.date(now.year - 1, WINTER[0][0], WINTER[0][1])
    first_winter_end_date = datetime.date(now.year, WINTER[1][0], WINTER[1][1])
    second_winter_start_date = datetime.date(now.year, WINTER[0][0], WINTER[0][1])

    # If we're in the middle of summer, remove the days passed of summer
    if summer_start_date < now < summer_end_date:
        threshold -= datetime.timedelta(days=(now - summer_start_date).days)
    # If the number of days between now and the end of the summer vacation is less than
    # the duration, we need to remove the length of summer from the threshhold
    elif 0 < (now - summer_end_date).days < DURATION:
        threshold -= datetime.timedelta(days=(summer_end_date - summer_start_date).days)
    # Same for middle of winter vacation, which will be after newyears
    elif first_winter_start_date < now < first_winter_end_date:
        threshold -= datetime.timedelta(days=(now - first_winter_start_date).days)
    # And for after the vacation
    elif 0 < (now - first_winter_end_date).days < DURATION:
        threshold -= datetime.timedelta(days=(first_winter_end_date - first_winter_start_date).days)
    # Then we need to check if we're into the start of the vacation this year, i.e. before newyears
    elif second_winter_start_date < now:
        threshold -= datetime.timedelta(days=(now - second_winter_start_date).days)

    # The returned value is a datetime object
    return datetime.datetime.combine(threshold, datetime.time())
