from django.db import models

class Redeem(models.Model):
  campaign_name = models.CharField(max_length=200, unique=False, verbose_name='Campaign name')
  redeem_code = models.CharField(max_length=32, blank=True, unique=True, verbose_name='Redeem code')
  redemption_address_type = models.IntegerField(verbose_name='Redemption address type')
  redemption_state = models.BooleanField(default=False, verbose_name='Redeemed')
  redemption_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name='Redemption date')

  def __str__(self):
    return f"{self.redeem_code}"
