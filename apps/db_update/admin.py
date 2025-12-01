from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.utils.html import format_html
from django.conf import settings
from common.errors import CompareDeltasError, InvalidAddressLength, InvalidBinFileError, InvalidJSONFileError, InvalidChainDBFile, InvalidTokenDBFile, InvalidTokenList, ProcessTokenError, SerializeDeltaError, ZipError, get_error_message
import datetime


# Register your models here.

from .models import DB
from .db_update import DBUpdate

DELTA_DBS = 500
class UpdateDBForm(forms.ModelForm):
    class Meta:
        model = DB
        fields = [
            'erc20_url',
            'chain_url',
            'abi_url',
            'version',
            'db_hash',
            'full_db_hash'
        ]
        widgets = {
            'erc20_url': forms.TextInput(),
            'chain_url': forms.TextInput(),
            'abi_url': forms.TextInput(),
            'version': forms.TextInput(attrs={'readonly': 'readonly'}),
            'db_hash': forms.HiddenInput(),
            'full_db_hash': forms.HiddenInput(),
        }

class UpdateDBAdmin(admin.ModelAdmin):
    list_display = ('erc20_url', 'chain_url', 'abi_url', 'creation_date', 'download_zip_file')
    form = UpdateDBForm

    def download_zip_file(self, obj):
        db_f_path = settings.MEDIA_URL + "/" + obj.version + "/" + obj.version + ".zip"
        res = format_html("<a href='{link}'>Download DB .zip</a>", link=db_f_path)
        return res

    def get_changeform_initial_data(self, request):
        last_entry = DB.objects.last()
        if last_entry:
            def_vals = {'erc20_url': last_entry.erc20_url, 'chain_url': last_entry.chain_url, 'abi_url': last_entry.abi_url}
        else:
             def_vals = {'erc20_url': None, 'chain_url': None, 'abi_url': None}

        def_vals["version"] = datetime.datetime.now().strftime("%Y%m%d")

        return def_vals

    def render_change_form(self, request, context, add=True, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_continue': False,
            'show_save_and_add_another': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        try:
            db_form_data = form.cleaned_data
            db_creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db = DBUpdate(erc20_url = db_form_data.get('erc20_url'), chain_url = db_form_data.get('chain_url'), abi_url = db_form_data.get('abi_url'), db_version = db_form_data.get('version'), creation_date=db_creation_date)
            db_file_hashes= db.upload_db()
            obj.db_hash = db_file_hashes['db_hash']
            obj.full_db_hash = db_file_hashes['full_db_hash']

            with transaction.atomic():
                if(obj.db_hash):
                    super().save_model(request, obj, form, change)
        except IntegrityError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "The database is already up-to-date" )          
        except (InvalidJSONFileError, ProcessTokenError, InvalidChainDBFile, InvalidTokenDBFile, Exception, InvalidAddressLength, InvalidTokenList, InvalidBinFileError, CompareDeltasError, SerializeDeltaError, ZipError) as err:
            DBUpdate.delete_db(obj.version)
            msg = get_error_message(err)
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, msg) 


    def has_change_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        DBUpdate.delete_db(obj.version)
        super().delete_model(request, obj)
   
    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Database List'}
        return super(UpdateDBAdmin, self).changelist_view(request, extra_context=extra_context)   
      
    def change_view(self, request, object_id, form_url='', extra_context=None):
      self.exclude = ('db_hash',)
      extra_context = extra_context or {}
      obj = self.get_object(request=request, object_id=object_id)
      extra_context['title'] = "Database " + obj.version
      extra_context['subtitle'] = ""

      return super(UpdateDBAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)   

admin.site.register(DB, UpdateDBAdmin)
admin.site.unregister(Group)
