from django.db import models
from django.core.exceptions import ValidationError

from common.utils import ishex

from secp256k1Crypto import PublicKey

def validate_uid(uid):
  if not ishex(uid):
    raise ValidationError("Invalid UID format")
  elif len(uid) != 32:
    raise ValidationError("Invalid UID length") 
  else:
    return uid
    
def validate_public_key(pub_key):
  if len(pub_key) == 66:
    try:
      PublicKey(bytes(bytearray.fromhex(pub_key)), raw=True)
    except Exception as err:
      raise ValidationError("Invalid public key")  
  else:
    raise ValidationError("Invalid public key length") 
   

class Device(models.Model):
  uid = models.CharField(max_length=32, unique=True, validators=[validate_uid], verbose_name='UID')
  public_key = models.CharField(max_length=66, unique=True, validators=[validate_public_key])
  verification_start_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name='First verification')
  success_counter = models.IntegerField(default=0, verbose_name='Counter')

  def __str__(self):
    return f"{self.uid}"
