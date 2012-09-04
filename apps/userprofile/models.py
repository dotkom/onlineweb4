from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class UserProfile(models.Model):
    #settings.py: AUTH_PROFILE_MODULE = "auth.UserProfile"
    user = models.ForeignKey(User, unique=True)

    is_online = models.BooleanField(_("is_online"))
    compiled = models.BooleanField(_("compiled"))

    def __unicode__(self):
        return u"Profile of user: %s" % self.user.username


# create userprofile when the user is created
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
