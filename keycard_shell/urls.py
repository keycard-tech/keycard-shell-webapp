"""
URL configuration for shell project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.site.site_header = "Keycard ShellAdmin"
admin.site.site_title = "Keycard Shell Admin"
admin.site.index_title = 'Keycard Shell Admin'

urlpatterns = [
  path('admin/', lambda r: redirect(f"/admin/db_update/db/")),
  path('admin/', admin.site.urls),
  path('', TemplateView.as_view(template_name="./keycard_shell/landing.html")),
  path('update/', include("apps.db_update.urls")),
  path('verify/', include("apps.device_verify.urls")),
  path('firmware/', include("apps.firmware_update.urls")),
  path('', include('pagedown.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
