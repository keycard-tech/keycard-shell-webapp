from django.urls import path

from . import views

app_name = "firmware"
urlpatterns = [
  path("release-notes", views.index, name="release-notes"),
  path("context", views.fw_context, name="firmware-context"),
  path("fws-context", views.fws_context, name="fws-context")
]