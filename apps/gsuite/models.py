# Kept since Django requires models.py to load apps.
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from apps.authentication.models import GroupRole, OnlineGroup

from .constants import GsuiteRoleType


class GsuiteGroup(models.Model):
    """
    Represents a group in Gsuite
    """

    email_name = models.CharField(_("E-postnavn"), max_length=128)
    main_group = models.ForeignKey(
        to=OnlineGroup,
        related_name="gsuite_group",
        verbose_name=_("Hovedgruppe"),
        on_delete=models.CASCADE,
    )

    """ Group's unique ID in Gsuite """
    gsuite_id = models.CharField(max_length=512, null=True, blank=True)
    """ Group's unique ETag in Gsuite """
    etag = models.CharField(max_length=512, null=True, blank=True)

    @property
    def email(self):
        gsuite_domain = settings.OW4_GSUITE_SYNC.get("DOMAIN")
        return f"{self.email_name}@{gsuite_domain}"

    @property
    def name(self):
        return self.main_group.name_long

    @property
    def description(self):
        return self.main_group.description_short

    def __str__(self):
        return f"{self.email} ({self.main_group})"


class GsuiteAlias(models.Model):
    email_name = models.CharField(_("E-postnavn"), max_length=128)
    gsuite_group = models.ForeignKey(
        to=GsuiteGroup,
        related_name="alias_set",
        verbose_name=_("Gsuite gruppe"),
        on_delete=models.CASCADE,
    )
    """ Group's unique ID in Gsuite """
    gsutie_id = models.CharField(max_length=512, null=True, blank=True)

    @property
    def email(self):
        gsuite_domain = settings.OW4_GSUITE_SYNC.get("DOMAIN")
        return f"{self.email_name}@{gsuite_domain}"

    def __str__(self):
        return self.email


class GroupSync(models.Model):
    """
    Relates an Online group to a Gsuite group
    An Online group can be synced to many groups in Gsuite
    """

    gsuite_group = models.ForeignKey(
        to=GsuiteGroup,
        related_name="sync_groups",
        verbose_name=_("Google-gruppe"),
        on_delete=models.CASCADE,
    )
    online_group = models.ForeignKey(
        to=OnlineGroup,
        related_name="gsuite_syncs",
        verbose_name=_("Online-gruppe"),
        on_delete=models.CASCADE,
    )
    """ Roles can be added to restrict syncing to a specific set of roles in a Group """
    roles = models.ManyToManyField(
        to=GroupRole,
        related_name="sync_groups",
        verbose_name=_("Synkroniserte roller"),
        blank=True,
    )
    """ Sync group members as a specific role """
    gsuite_role = models.CharField(
        verbose_name=_("Rolle i Gsuite"),
        max_length=64,
        default=GsuiteRoleType.MEMBER,
        choices=GsuiteRoleType.ALL_CHOICES,
    )

    def __str__(self):
        return f"{self.online_group} - {self.gsuite_group}"
