from django.core.exceptions import ValidationError
import pyotp
from .models import UserTwoFactorAuth


def user_two_factor_auth_data_create(*, user):
  if hasattr(user, 'two_factor_auth_data'):
    raise ValidationError( '2FA is already in use')

  two_factor_auth_data = UserTwoFactorAuth.objects.create(user=user, otp_secret=pyotp.random_base32())

  return two_factor_auth_data
