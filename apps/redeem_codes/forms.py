from django import forms

from apps.redeem_codes.models import Address, Campaign
from common.consts import REDEEM_ADDRESSES

class CampaignAddForm(forms.ModelForm):
  code_prefix = forms.CharField(max_length=10, required=False)
  quantity = forms.IntegerField(required=True, min_value=1, initial=1)
  
  class Meta:
    model = Campaign
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
      'quantity': forms.NumberInput(),
      'redemption_state': forms.HiddenInput(),
      'redemption_date': forms.HiddenInput(),
    }
  
class CampaignChangeForm(forms.ModelForm):
  class Meta:
    model = Campaign
    fields = [
      'campaign_name',
      'redeem_code',
      'redemption_address_type',
      'redemption_state',
      'redemption_date'
    ]
    
class AddressAddForm(forms.ModelForm):
  redemption_address_type = forms.ChoiceField(required=True, choices=REDEEM_ADDRESSES)
  
  class Meta:
    model = Address
    fields = [
        'campaign_name',
        'redemption_address'
    ]
    widgets = {
        'campaign_name': forms.TextInput(),
        'redemption_address_type': forms.Select(),
        'redemption_address': forms.TextInput()
    }  
    
class AddressChangeForm(forms.ModelForm):
  class Meta:
    model = Address
    fields = [
      'campaign_name',
      'redemption_address'
    ]  
    
class ExportCodesAsCSVForm(forms.Form):
  campaign = forms.ChoiceField(required=True, choices=None, widget=forms.Select(attrs={'class': 'admin__export-form-select'}))
  
  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campaigns_list = Campaign.objects.all().values_list('campaign_name', flat=True).distinct()
        self.fields["campaign"].choices = [(campaign, campaign) for campaign in campaigns_list]
class ExportAddressesAsCSVForm(forms.Form):
  campaign = forms.ChoiceField(required=True, choices=None, widget=forms.Select(attrs={'class': 'admin__export-form-select'}))  
  
  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campaigns_list = Address.objects.all().values_list('campaign_name', flat=True).distinct()
        self.fields["campaign"].choices = [(campaign, campaign) for campaign in campaigns_list]
    
    