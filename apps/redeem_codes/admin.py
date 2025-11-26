from django.urls import path
from django.contrib import admin
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.http import HttpResponse
from django.template.response import TemplateResponse

from apps.redeem_codes.forms import AddressAddForm, AddressChangeForm, CampaignAddForm, CampaignChangeForm, ExportAddressesAsCSVForm, ExportCodesAsCSVForm
from common.consts import REDEEM_ADDRESSES, REDEMPTION_LINK
from common.errors import get_error_message

from .models import Campaign, Address, validate_redemption_address

import secrets
import base64
import csv

class ExportCsvMixin:
    def export_csv_form(self, request, export_form, export_context, is_campaign, model):
      if request.method == "POST":
          form = export_form(request.POST)
          if form.is_valid():
              c_name = form.cleaned_data["campaign"]
              campaign = model.objects.all().filter(campaign_name=c_name)
              return self.export_as_csv(request, is_campaign, campaign, c_name)
      
      context = export_context

      return TemplateResponse(request, "admin/redeem_export.html", context)
      
    def export_as_csv(self, request, is_campaign, queryset, c_name):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
          
        if is_campaign:
          field_names.append('redemption_link')
            
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(c_name)
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
          if is_campaign:
            redemption_link = '{}/{}/{}'.format(REDEMPTION_LINK, obj.campaign_name, obj.redeem_code)
            obj.redemption_address_type = REDEEM_ADDRESSES[obj.redemption_address_type]
          writer.writerow([getattr(obj, field) if field != 'redemption_link' else redemption_link  for field in field_names])

        return response

class RedeemAddressAdmin(admin.ModelAdmin, ExportCsvMixin):
  list_display = ('campaign_name', 'redemption_address')
  form = AddressChangeForm
  add_form = AddressAddForm 
  
  change_list_template = "admin/redeem_changelist.html"
  
  def get_urls(self):
      urls = super().get_urls()
      custom_urls = [
        path('export/', self.export_addresses_as_csv),
      ]
      return custom_urls + urls
  
  def get_form(self, request, obj=None, **kwargs):
      defaults = {}
      if obj is None:
          defaults['form'] = self.add_form
      defaults.update(kwargs)
      return super().get_form(request, obj, **defaults)
  
  def export_addresses_as_csv(self, request):
      export_form = ExportAddressesAsCSVForm
      
      context = dict(
        self.admin_site.each_context(request),
        opts=Address._meta,
        title="Export Redemption Addresses",
        form=ExportAddressesAsCSVForm(),
      )
      
      return self.export_csv_form(request, export_form, context, False, Address)
  
  def save_model(self, request, obj, form, change):
    try:
      redeem_form_data = form.cleaned_data
      obj = Address(campaign_name=redeem_form_data.get('campaign_name'), redemption_address=validate_redemption_address(redeem_form_data.get("redemption_address"), REDEEM_ADDRESSES[int(redeem_form_data.get("redemption_address_type"))]))
      with transaction.atomic():
        super().save_model(request, obj, form, change)
    except IntegrityError as err:
      messages.set_level(request, messages.ERROR)
      messages.add_message(request, messages.ERROR, "Redeem address already exists")          
    except Exception as err:
      messages.set_level(request, messages.ERROR)
      messages.add_message(request, messages.ERROR, err)  
  
  def has_change_permission(self, request, obj=None):
    return False

class RedeemCampaignAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_filter = ["campaign_name"]
    list_display = ('campaign_name', 'redeem_code', 'redemption_address_type_display', 'redemption_state', 'redemption_date')
    
    change_list_template = "admin/redeem_changelist.html"
    
    @admin.display(description='Address type')
    def redemption_address_type_display(self, obj):
        return REDEEM_ADDRESSES[obj.redemption_address_type]
    
    form = CampaignChangeForm
    add_form = CampaignAddForm
    
    def get_urls(self):
      urls = super().get_urls()
      custom_urls = [path('export/', self.export_campaign_as_csv)]
      return custom_urls + urls
    
    def get_form(self, request, obj=None, **kwargs):
      defaults = {}
      if obj is None:
          defaults['form'] = self.add_form
      defaults.update(kwargs)
      return super().get_form(request, obj, **defaults)
    
    def export_campaign_as_csv(self, request):
      export_form = ExportCodesAsCSVForm
      
      context = dict(
        self.admin_site.each_context(request),
        opts=Address._meta,
        title="Export Campaign",
        form=ExportCodesAsCSVForm(),
      )
      
      return self.export_csv_form(request, export_form, context, True, Campaign)  
      
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
        return super(RedeemCampaignAdmin, self).changelist_view(request, extra_context=extra_context)
      
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
            if r_code:
              redeem_code = Campaign(
                campaign_name=redeem_form_data.get('campaign_name'),
                redeem_code=r_code,
                redemption_address_type=redeem_form_data.get('redemption_address_type'),
              )
              data.append(redeem_code)
          if data:  
            Campaign.objects.bulk_create(data)   
            self.message_user(request, "Redeem codes created successfully") 
        except IntegrityError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "Redeem code already exists")          
        except Exception as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, err)  

admin.site.register(Campaign, RedeemCampaignAdmin)
admin.site.register(Address, RedeemAddressAdmin)