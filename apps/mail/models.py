from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class MommyUserConfig(models.Model):
    user = models.ForeignKey(User)
    task = models.CharField(_(u'Oppgave'), max_length=100)  # class.__name__
    email = models.BooleanField(_(u'Motta email'))
    notification = models.BooleanField(_(u'Motta notification'))

class Notification(models.Model):
    user = models.ForeignKey(User)
    message = models.CharField(_(u'Melding'), max_length=1000)
