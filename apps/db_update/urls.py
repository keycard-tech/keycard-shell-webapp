from django.urls import path
from . import views

app_name = "db"
urlpatterns = [
  path("", views.index, name="update-index"),
  path("air-gapped", views.air_gapped_update, name="air-gapped-update"),
  path("db-version-history", views.release_notes, name="db-version-history"),
  path("get-db", views.get_current_db, name="get-db"),
  path("get-dbs", views.get_dbs, name="get-dbs")
]