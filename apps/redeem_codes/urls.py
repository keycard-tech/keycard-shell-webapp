from django.urls import path

from . import views

app_name = "redeem"
urlpatterns = [
  path("<str:campaign_name>/<str:redeem_code>", views.index, name="redeem-index"),
  path("verify-redeem", views.redeem, name="verify-redeem")
]
