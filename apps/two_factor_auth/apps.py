from django.apps import AppConfig
from django.contrib.auth.apps import AuthConfig

class TwoFactorAuthConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'apps.two_factor_auth'
  AuthConfig.verbose_name = "Authentication"
