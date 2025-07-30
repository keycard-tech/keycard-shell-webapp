from django import forms

from apps.device_verify.models import Device, validate_public_key, validate_uid

class DeviceVerifyForm(forms.ModelForm):
  uid = forms.CharField(max_length=100)
  public_key = forms.CharField(max_length=100)
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
      super(DeviceVerifyForm, self).__init__(*args, **kwargs)
      self.fields['public_key'].help_text = 'Insert a valid 66-bit hex string'
      self.fields['uid'].help_text = 'Insert a valid 32-bit hex string'
      self.fields['uid'].widget.attrs.pop('maxlength', None)
      self.fields['public_key'].widget.attrs.pop('maxlength', None)
      
  def clean_uid(self):
    self.cleaned_data['uid'] = validate_uid(self.cleaned_data.get('uid'))
    return self.cleaned_data['uid']  
  
  def clean_public_key(self):
    self.cleaned_data['public_key'] = validate_public_key(self.cleaned_data.get('public_key'))
    return self.cleaned_data['public_key']   
  
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