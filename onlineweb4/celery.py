import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineweb4.settings')

app = Celery('onlineweb4')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
