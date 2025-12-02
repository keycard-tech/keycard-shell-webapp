from django.db import models
from django.core.exceptions import ValidationError
from common.consts import REDEEM_ADDRESSES

import re
import coinaddr  

def validate_campaign_name(str):
  if re.match(r'^[a-zA-Z0-9_-]+$', str) is not None:
    return str
  else:
    raise ValidationError("Campaign name must be url safe")
  
def validate_redemption_address(address, address_type):
  val = coinaddr.validate(address_type.lower(), address.encode('utf-8'))
  if val.valid:
    return address
  elif address_type == "Bitcoin":
    return validate_redemption_address(address, "btc-segwit")
  else:
    raise ValidationError("Invalid {} address".format(address_type) )
  
class Campaign(models.Model):
  class Meta:
    verbose_name = "Codes"
    verbose_name_plural = "Codes"
    
  campaign_name = models.CharField(max_length=200, unique=False, verbose_name='Campaign name', validators=[validate_campaign_name])
  redeem_code = models.CharField(max_length=48, blank=True, unique=True, verbose_name='Redeem code')
  redemption_address_type = models.IntegerField(verbose_name='Redemption address type')
  redemption_state = models.BooleanField(default=False, verbose_name='Redeemed')
  redemption_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name='Redemption date')

  def __str__(self):
    return f"{self.redeem_code}"
  
class Address(models.Model):
  class Meta:
    verbose_name = "Address"
    verbose_name_plural = "Addresses"
    
  campaign_name = models.CharField(max_length=200, unique=False, verbose_name='Campaign name', validators=[validate_campaign_name])
  redemption_address = models.CharField(max_length=42, unique=False, verbose_name='Redemption address')
  
  def __str__(self):
    return f"{self.redemption_address}"
