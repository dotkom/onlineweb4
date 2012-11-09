#-*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Mark(models.Model):
    CATEGORY_CHOICES = (
        (0, _("Ingen")),
        (1, _("Sosialt")),
        (2, _("Bedriftspresentasjon")),
        (3, _("Kurs")),
        (4, _("Tilbakemelding")),
        (5, _("Kontoret")),
    )

    title = models.CharField(_("tittel"), max_length=50)
    given_to = models.ManyToManyField(User, null=True, blank=True,
        through="UserEntry", verbose_name=_("gitt til"))
    mark_added_date = models.DateTimeField(_("utdelt dato"), auto_now_add=True)
    given_by = models.ForeignKey(User, related_name="mark_given_by", verbose_name=_("gitt av"), editable=False)
    last_changed_date = models.DateTimeField(_("sist redigert"), auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(User, related_name="marks_last_changed_by",
        verbose_name=_("sist redigert av"), editable=False)
    description = models.CharField(_("beskrivelse"), max_length=100, 
        help_text=_("Hvis dette feltet etterlates blankt vil det fylles med "
        "en standard grunn for typen prikk som er valgt."),
        blank=True)
    category = models.SmallIntegerField(_("kategori"), choices=CATEGORY_CHOICES, default=0)

    def __unicode__(self):
        return _("Prikk for %s") % self.title

    class Meta:
        verbose_name = _("Prikk")
        verbose_name_plural = _("Prikker")

class UserEntry(models.Model):
    user = models.ForeignKey(User)
    mark = models.ForeignKey(Mark)

    def __unicode__(self):
        return _("UserEntry for %s") % self.user.get_full_name()

    class Meta:
        unique_together = ("user", "mark")
