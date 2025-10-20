from django.contrib import admin
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponse

from apps.redeem_codes.forms import RedeemForm, RedeemChangeForm
from common.consts import REDEEM_ADDRESSES, REDEMPTION_LINK
from common.errors import get_error_message

from .models import Redeem

import secrets
import base64
import csv

class ExportCsvMixin:
    def export_campaign_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        field_names.append('redemption_link')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(queryset.first().campaign_name)
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
          redemption_link = '{}/{}/{}'.format(REDEMPTION_LINK, obj.campaign_name, obj.redeem_code)
          obj.redemption_address_type = REDEEM_ADDRESSES[obj.redemption_address_type]
          writer.writerow([getattr(obj, field) if field != 'redemption_link' else redemption_link  for field in field_names])

        return response

    export_campaign_as_csv.short_description = "Export Selected Campaign"

class RedeemAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_filter = ["campaign_name"]
    list_display = ('campaign_name', 'redeem_code', 'redemption_address_type_display', 'redemption_state', 'redemption_date')
    actions = ["export_campaign_as_csv"]
    
    @admin.display(description='Address type')
    def redemption_address_type_display(self, obj):
        return REDEEM_ADDRESSES[obj.redemption_address_type]
    
    form = RedeemChangeForm
    add_form = RedeemForm
    
    def get_form(self, request, obj=None, **kwargs):
      defaults = {}
      if obj is None:
          defaults['form'] = self.add_form
      defaults.update(kwargs)
      return super().get_form(request, obj, **defaults)

    def has_change_permission(self, request, obj=None):
      return False

    def render_change_form(self, request, context, add=True, change=False, form_url='', obj=None):
      context.update({
        'show_save_and_continue': False,
        'show_save_and_add_another': False
      })
      return super().render_change_form(request, context, add, change, form_url, obj)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Redeem Codes List'}
        return super(RedeemAdmin, self).changelist_view(request, extra_context=extra_context)
      
    def change_view(self, request, object_id, form_url='', extra_context=None):
      extra_context = extra_context or {}
      obj = self.get_object(request=request, object_id=object_id)
      extra_context['title'] = obj.redeem_code
      extra_context['subtitle'] = ""

      return super().change_view(request, object_id, form_url, extra_context=extra_context)   
    
    def save_model(self, request, obj, form, change):
        try:
          redeem_form_data = form.cleaned_data
          codesCount = redeem_form_data.get('quantity')
          data = []
          for i in range(codesCount):
            code = base64.b32encode(secrets.token_bytes(16)).replace(b'=', b'').decode("ascii")
            r_code = redeem_form_data.get('code_prefix').upper() + code
            if(r_code):
              redeem_code = Redeem(
                campaign_name=redeem_form_data.get('campaign_name'),
                redeem_code=r_code,
                redemption_address_type=redeem_form_data.get('redemption_address_type'),
              )
              data.append(redeem_code)
          if data:  
            Redeem.objects.bulk_create(data)   
            self.message_user(request, "Redeem codes created successfully") 
        except IntegrityError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "Redeem code already exists")          
        except (Exception) as err:
            msg = get_error_message(err)
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, msg)  

admin.site.register(Redeem, RedeemAdmin)