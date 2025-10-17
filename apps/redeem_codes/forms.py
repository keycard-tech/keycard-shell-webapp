from django import forms

from apps.redeem_codes.models import Redeem
from common.consts import REDEEM_ADDRESSES

class RedeemForm(forms.ModelForm):
  code_prefix = forms.CharField(max_length=10, required=False)
  
  class Meta:
    model = Redeem
    fields = [
      'campaign_name',
      'redeem_code',
      'redemption_address_type',
      'redemption_state',
      'redemption_date'
    ]
    widgets = {
      'campaign_name': forms.TextInput(),
      'code_prefix': forms.TextInput(),
      'redeem_code': forms.HiddenInput(),
      'redemption_address_type': forms.Select(choices=REDEEM_ADDRESSES),
      'redemption_state': forms.HiddenInput(),
      'redemption_date': forms.HiddenInput(),
    }
  
class RedeemChangeForm(forms.ModelForm):
  class Meta:
    model = Redeem
    fields = [
      'campaign_name',
      'redeem_code',
      'redemption_address_type',
      'redemption_state',
      'redemption_date'
    ]
    widgets = {
      'campaign_name': forms.TextInput(),
      'redeem_code': forms.TextInput(),
      'redemption_address_type': forms.Select(choices=REDEEM_ADDRESSES),
      'redemption_state': forms.CheckboxInput(attrs={'readonly': 'readonly'}),
      'redemption_date': forms.TextInput(attrs={'readonly': 'readonly'}),
    }   