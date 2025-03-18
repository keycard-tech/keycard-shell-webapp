import uuid
from django.db import models
from django.conf import settings
from encrypted_fields.fields import EncryptedCharField
import pyotp
import qrcode
import qrcode.image.svg


class UserTwoFactorAuth(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='two_factor_auth_data', on_delete=models.CASCADE)
    otp_secret = EncryptedCharField(max_length=64)
    session_identifier = models.UUIDField(blank=True, null=True)

    def generate_qr_code(self, name = None):
        totp = pyotp.TOTP(self.otp_secret)
        qr_uri = totp.provisioning_uri(name=name, issuer_name='Keycard Shell Admin')

        image_factory = qrcode.image.svg.SvgPathImage
        qr_code_image = qrcode.make(qr_uri, image_factory=image_factory)

        return qr_code_image.to_string().decode('utf_8')
    
    def validate_otp(self, otp: str) -> bool:
        totp = pyotp.TOTP(self.otp_secret)

        return totp.verify(otp)
    def rotate_session_identifier(self):
        self.session_identifier = uuid.uuid4()

        self.save(update_fields=["session_identifier"])