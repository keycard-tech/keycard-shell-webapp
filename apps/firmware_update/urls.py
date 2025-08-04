from django.urls import path

from . import views

app_name = "firmware"
urlpatterns = [
  path("release-notes", views.index, name="release-notes"),
  path("get-firmware", views.get_current_firmware, name="get-firmware"),
  path("get-firmwares", views.get_firmwares, name="get-firmwares")
]