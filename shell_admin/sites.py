from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import path, reverse

from apps.two_factor_auth.models import UserTwoFactorAuth
from apps.two_factor_auth.views import AdminConfirmTwoFactorAuthView, AdminSetupTwoFactorAuthView


class AdminSite(admin.AdminSite):
  def get_urls(self):
    base_urlpatterns = super().get_urls()

    extra_urlpatterns = [
      path("setup-two-factor-auth/", self.admin_view(AdminSetupTwoFactorAuthView.as_view()), name="setup-two-factor-auth"),
      path("confirm-two-factor-auth/", self.admin_view(AdminConfirmTwoFactorAuthView.as_view()), name="confirm-two-factor-auth"),
  ]

    return extra_urlpatterns + base_urlpatterns

  def login(self, request, *args, **kwargs):
    if request.method != "POST":
      return super().login(request, *args, **kwargs)

    username = request.POST.get("username")

    two_factor_auth_data = UserTwoFactorAuth.objects.filter(user__username=username).first()

    request.POST._mutable = True
    request.POST[REDIRECT_FIELD_NAME] = reverse("admin:confirm-two-factor-auth")

    if two_factor_auth_data is None:
      request.POST[REDIRECT_FIELD_NAME] = reverse("admin:setup-two-factor-auth")

    request.POST._mutable = False

    return super().login(request, *args, **kwargs)

  def has_permission(self, request):
    has_perm = super().has_permission(request)

    if not has_perm:
      return has_perm

    two_factor_auth_data = UserTwoFactorAuth.objects.filter(user=request.user).first()

    allowed_paths = [reverse("admin:confirm-two-factor-auth"), reverse("admin:setup-two-factor-auth")]

    if request.path in allowed_paths:
      return True

    if two_factor_auth_data is not None:
      two_factor_auth_token = request.session.get("two_factor_auth_token")
      return str(two_factor_auth_data.session_identifier) == two_factor_auth_token

    return False