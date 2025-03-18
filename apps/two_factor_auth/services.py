from django.core.exceptions import ValidationError
import pyotp
from .models import UserTwoFactorAuth


def user_two_factor_auth_data_create(*, user):
    if hasattr(user, 'two_factor_auth_data'):
        raise ValidationError( 'Can not have more than one 2FA related data.')

    two_factor_auth_data = UserTwoFactorAuth.objects.create(user=user, otp_secret=pyotp.random_base32())

    return two_factor_auth_data
