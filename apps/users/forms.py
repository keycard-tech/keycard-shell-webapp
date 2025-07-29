from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import CheckboxInput, HiddenInput, TextInput

from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
          'username', 
          'email', 
          'is_active',
          'is_superuser', 
          'is_staff', 
        ]
        widgets = {
          'username': TextInput(),
          'email': TextInput(),
          'is_active': CheckboxInput,
          'is_staff': HiddenInput(attrs={'value': True}),
          'is_superuser': HiddenInput(attrs={'value': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['is_superuser'] = True   
        self.initial['is_staff'] = True  
        self.fields['password2'].label = 'Repeat password'
        self.fields['password1'].help_text = 'Create a password with at least 8 characters. Use at least 1 digit, 1 special character and 1 uppercase letter.'
        self.fields['password2'].help_text = 'Repeat password'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
          "username", 
          "email", 
          "is_active",
          "is_superuser", 
          "is_staff", 
        ]
        widgets = {
            'username': TextInput(),
            'email': TextInput(),
            'is_active': CheckboxInput,
            'is_staff': HiddenInput(),
            'is_superuser': HiddenInput(),
        }
        