from django.contrib.admin.apps import AdminConfig as BaseAdminConfig


class ShellAdminConfig(BaseAdminConfig):
    default_site = "shell_admin.sites.AdminSite"