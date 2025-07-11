from django.urls import path

from . import views

app_name = "firmware"
urlpatterns = [
  path("context", views.fw_context, name="firmware-context")
]