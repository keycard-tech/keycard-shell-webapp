from django.apps import AppConfig

class DbUpdateConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'apps.db_update'
  verbose_name_plural = 'DB'
  verbose_name = 'ERC20 & Chain Database'
