from django.urls import re_path

from apps.mailinglists import views

urlpatterns = [re_path(r"^$", views.index, name="mailinglists_index")]
