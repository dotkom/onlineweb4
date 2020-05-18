from django.conf.urls import url

from apps.contact import views

urlpatterns = [
    url(r"^$", views.index, name="contact_index"),
    url(r"^submit/", views.contact_submit, name="submit"),
]
