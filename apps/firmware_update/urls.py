from django.urls import path

from . import views

app_name = "firmware"
urlpatterns = [
  path("", views.index, name="firmware-index"),
  path("context", views.fw_context, name="firmware-context")
]