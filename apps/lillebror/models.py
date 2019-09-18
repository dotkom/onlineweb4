from django.db import models

class Permissions(models.Model):
    permission_text = models.CharField(max_length=200)
