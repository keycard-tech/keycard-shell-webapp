from django.contrib import admin
from django import forms
from django.urls import path
from django.db import IntegrityError
from django.contrib import messages
import csv
from django.shortcuts import redirect
import codecs

# Register your models here.

from .models import Device, validate_uid
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
      'verification_start_date': forms.TextInput(attrs={'readonly': 'readonly'}),
      'success_counter': forms.TextInput(attrs={'readonly': 'readonly'}),
    }
class DeviceVerifyAdmin(admin.ModelAdmin):
    list_display = ('uid', 'public_key', 'verification_start_date', 'success_counter')
    form = DeviceVerifyForm
    change_list_template = "admin/devices_changelist.html"

    def get_urls(self):
      urls = super().get_urls()
      custom_urls = [
        path('import-csv/', self.import_csv),
      ]
      return custom_urls + urls

    def import_csv(self, request):
      try:
        if request.method == "POST":
          csv_file = request.FILES["csv_file"]
          reader = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
          data = []
          for uid, public_key in reader:
              device = Device(uid=validate_uid(uid), public_key=validate_uid(public_key), verification_start_date=None, success_counter=0)
              data.append(device)
          Device.objects.bulk_create(data)   
          self.message_user(request, "CSV file imported successfully")  
      except IntegrityError as err:
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, "Device already exists. Please check your csv.")           
      except csv.Error as err:
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, f"Error: {err}")
      except UnicodeDecodeError:
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, "The CSV file contains characters that cannot be decoded.")
      except (FileNotFoundError, Exception) as err:
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, f"Error reading CSV file. {err}")

      return redirect('/admin/device_verify/device')    

    def has_change_permission(self, request, obj=None):
      return False

    def render_change_form(self, request, context, add=True, change=False, form_url='', obj=None):
      context.update({
        'show_save_and_continue': False,
        'show_save_and_add_another': False
      })
      return super().render_change_form(request, context, add, change, form_url, obj)

admin.site.register(Device, DeviceVerifyAdmin)

