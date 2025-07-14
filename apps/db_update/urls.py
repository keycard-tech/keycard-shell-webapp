from django.urls import path
from . import views

app_name = "db"
urlpatterns = [
  path("", views.index, name="update-index"),
  path("db-release-notes", views.release_notes, name="db-release-notes"),
  path("context", views.db_context, name="db-context"),
  path(".well-known/acme-challenge/HzV4pDh6R9Y1YE7cQL_I7vGzKj9oVdyeF5qgxWCjDZM", views.security_txt)
]