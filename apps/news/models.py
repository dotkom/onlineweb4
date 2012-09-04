from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class News(models.Model):
    title = models.CharField(_("title"), max_length=50)
    author = models.ForeignKey(User, verbose_name=_("author"), editable=False)
    text = models.TextField(_("text"))

    post_date = models.DateTimeField(_("posted date"), auto_now_add=True)
    last_edited_date = models.DateTimeField(_("last edited"), auto_now=True)
    last_edited_by = models.ForeignKey(User, verbose_name=_("last edited by"),
        editable=False, related_name="last_news_edits")
    expiration_date = models.DateTimeField(_("expiration date"))
