from django.contrib import admin, messages
from django import forms
from django.shortcuts import redirect
from pagedown.widgets import AdminPagedownWidget
from django.db import IntegrityError, transaction
from django.conf import settings

from common.errors import InvalidFirmwareError, get_error_message

from .models import Firmware
from common.utils import makedirs
from .firmware import calc_fw_hash, upload_file, delete_fw, validate_firmware
class FirmwareForm(forms.ModelForm):
  firmware = forms.FileField(widget=forms.FileInput(attrs={"accept": ".bin"}))
  changelog = forms.CharField(widget=AdminPagedownWidget())

  class Meta:
    model = Firmware
    fields = [
        'version',
        'fw_hash'
    ]
    widgets = {
        'version': forms.TextInput(),
        'fw_hash': forms.HiddenInput()
    }
class FirmwareAdmin(admin.ModelAdmin):
    form = FirmwareForm

    def get_form(self, request, obj, **kwargs):
      form = super(FirmwareAdmin, self).get_form(request, obj, **kwargs)
      try:
        if obj != None:
          fw_version = obj.version
          chl_p = settings.MEDIA_ROOT + '/' + fw_version + '/changelog.md'

          form.base_fields['version'].disabled = True
          form.base_fields['fw_hash'].widget = forms.Textarea(attrs={'readonly': 'readonly', 'rows': '1', 'class': 'admin__fw_hash'})
          form.base_fields['firmware'].required = False

          with open(chl_p, encoding="utf-8") as f:
            form.base_fields['changelog'].initial = f.read()
        else:
          form.base_fields['changelog'].initial = ""
          form.base_fields['firmware'].required = True     
      except (FileNotFoundError, Exception) as err:
        msg = get_error_message(err)
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, msg) 

      return form

    def get_fields(self, request, obj=None):
      fields = super(FirmwareAdmin, self).get_fields(request, obj)
      fields_list = list(fields)

      if obj:
        fields_list.remove('firmware')

      fields_tuple = tuple(fields_list)
      return fields_tuple

    def save_model(self, request, obj, form, change):
      try:
        form_data = form.cleaned_data
        fw = form_data["firmware"]
        chl = form_data["changelog"]
        output_dir = settings.MEDIA_ROOT + '/' + form_data["version"]
        

        makedirs(output_dir)

        changelog_output = output_dir + '/changelog.md'
        upload_file(chl, changelog_output, "w", "utf-8", "\n")

        if fw:
          fw_file = fw.file.getvalue()
          fw_output = output_dir + '/firmware.bin'
          if validate_firmware(fw_file, form_data["version"]):
            upload_file(fw_file, fw_output, "wb", None, None)
            obj.fw_hash = calc_fw_hash(fw_file)
            with transaction.atomic():
              super().save_model(request, obj, form, change)
      except IntegrityError as err:
        delete_fw(form_data["version"]) 
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, f"Firmware {form_data["version"]}  already exists")        
      except(InvalidFirmwareError, Exception)  as err:
        delete_fw(form_data["version"])  
        msg = get_error_message(err)
        messages.set_level(request, messages.ERROR)
        messages.add_message(request, messages.ERROR, msg)     

    def render_change_form(self, request, context, add=True, change=True, form_url='', obj=None):
      context.update({
        'show_save_and_continue': False,
        'show_save_and_add_another': False
      })
      return super().render_change_form(request, context, add, change, form_url, obj)

    def delete_model(self, request, obj):
      delete_fw(obj.version)
      super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
      with transaction.atomic():
        for obj in queryset:
          delete_fw(obj.version)
      return super().delete_queryset(request, queryset)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Firmware List'}
        return super(FirmwareAdmin, self).changelist_view(request, extra_context=extra_context)
      
    def change_view(self, request, object_id, form_url='', extra_context=None):
      extra_context = extra_context or {}
      obj = self.get_object(request=request, object_id=object_id)
      extra_context['title'] = "Firmware " + obj.version
      extra_context['subtitle'] = ""

      return super().change_view(request, object_id, form_url, extra_context=extra_context)     

admin.site.register(Firmware, FirmwareAdmin)

