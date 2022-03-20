from django.urls import re_path

from apps.contact import views

urlpatterns = [
    re_path("^$", views.index, name="contact_index"),
    re_path("^submit/", views.contact_submit, name="submit"),
]
