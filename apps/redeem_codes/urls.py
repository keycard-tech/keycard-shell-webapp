from django.urls import path

from . import views

app_name = "redeem"
urlpatterns = [
  path("", views.index, name="index")
]