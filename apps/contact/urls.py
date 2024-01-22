from django.urls import re_path

from apps.contact import views

urlpatterns = [
    re_path(r"^$", views.index, name="contact_index"),
    re_path(r"^submit/", views.contact_submit, name="submit"),
]
