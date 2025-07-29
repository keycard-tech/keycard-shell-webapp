from django import forms

from apps.device_verify.models import Device

class DeviceVerifyForm(forms.ModelForm):
  class Meta:
    model = Device
    fields = [
      'uid',
      'public_key',
      'verification_start_date',
      'success_counter'
    ]
    widgets = {
      'uid': forms.TextInput(),
      'public_key': forms.TextInput(),
      'verification_start_date': forms.HiddenInput(),
      'success_counter': forms.HiddenInput(),
    }
    
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['public_key'].help_text = 'Insert a valid 66-bit hex string'
      self.fields['uid'].help_text = 'Insert a valid 32-bit hex string'
      
class DeviceVerifyChangeForm(forms.ModelForm):
  class Meta:
    model = Device
    fields = [
      'uid',
      'public_key',
      'verification_start_date',
      'success_counter'
    ]
    widgets = {
      'uid': forms.TextInput(),
      'public_key': forms.TextInput(),
      'verification_start_date': forms.TextInput(attrs={'readonly': 'readonly'}),
      'success_counter': forms.TextInput(attrs={'readonly': 'readonly'}),
    }   