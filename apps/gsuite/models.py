from django.db import models

class ServiceAccount(models.Model):
  type = models.CharField(max_length=80, default="service_account")
  project_id = models.CharField(max_length=80)
  private_key_id = models.CharField(max_length=80)
  private_key = models.TextField()
  client_email = models.EmailField(max_length=80)
  client_id = models.CharField(max_length=80)
  auth_uri = models.CharField(max_length=80)
  token_uri = models.CharField(max_length=80)
  auth_provider_x509_cert_url = models.CharField(max_length=80)
  client_x509_cert_url = models.CharField(max_length=80)
