from django.db import models


class Repository(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=300)
    url = models.URLField()
    updated_at = models.DateTimeField()


class RepositoryLanguage(models.Model):
    repository = models.ForeignKey(Repository, related_name='languages', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    size = models.IntegerField()
