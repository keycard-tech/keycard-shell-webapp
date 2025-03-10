from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.admin.models import LogEntry
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.utils.html import format_html
from django.conf import settings
from common.errors import CompareDeltasError, DecodeEntryError, InvalidAddressLength, InvalidBinFileError, InvalidJSONFileError, InvalidChainDBFile, InvalidTokenDBFile, InvalidTokenList, ProcessTokenError, SerializeDeltaError, ZipError
from common.utils import iter_query
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
            'version',
            'db_hash'
        ]
        widgets = {
            'erc20_url': forms.TextInput(),
            'chain_url': forms.TextInput(),
            'version': forms.TextInput(attrs={'readonly': 'readonly'}),
            'db_hash': forms.HiddenInput(),
        }

class UpdateDBAdmin(admin.ModelAdmin):
    list_display = ('erc20_url', 'chain_url', 'creation_date', 'download_db_files')
    form = UpdateDBForm

    def download_db_files(self, obj):
        db_f_path = settings.MEDIA_URL + "/" + obj.version + "/" + obj.version + ".zip"
        res = format_html("<a href='{link}'>Download DB files</a>", link=db_f_path)
        return res

    def get_changeform_initial_data(self, request):
        last_entry = DB.objects.last()
        if last_entry:
            def_vals = {'erc20_url': last_entry.erc20_url, 'chain_url': last_entry.chain_url}
        else:
             def_vals = {'erc20_url': None, 'chain_url': None, }

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
            d = form.cleaned_data
            dbs_query = DB.objects.all().order_by('-version')[:DELTA_DBS]
            prev_dbs = iter_query(dbs_query, "version")
            db = DBUpdate(erc20_url = d.get('erc20_url'), chain_url = d.get('chain_url'), db_version = d.get('version'), prev_dbs = prev_dbs)
            f_hash = db.upload_db()
            obj.db_hash = f_hash

            with transaction.atomic():
                if(obj.db_hash):
                    super().save_model(request, obj, form, change)
        except IntegrityError as err:
            DBUpdate.delete_db(obj.version)
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "The database is already up-to-date")
        except InvalidJSONFileError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "Invalid JSON at " +  err.path) 
        except ProcessTokenError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Error processing token. {err.err}")      
        except InvalidChainDBFile as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Can't create db.bin. Error: {err.err}") 
        except InvalidTokenDBFile as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Can't create db.bin. Error: {err.err}")     
        except InvalidAddressLength  as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "Unexpected address format") 
        except InvalidTokenList as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, "Processing token list. Error: Invalid JSON")     
        except InvalidBinFileError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Invalid bin file at {err.path}")    
        except CompareDeltasError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Error comparing {err.prev_db} and {err.latest_db}")   
        except SerializeDeltaError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Unable to create {err.delta_version} delta") 
        except ZipError as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, f"Unable to zip {err.path}")      
        except Exception as err:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, err) 


    def has_change_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        DBUpdate.delete_db(obj.version)
        super().delete_model(request, obj)

admin.site.register(DB, UpdateDBAdmin)
admin.site.unregister(Group)


admin.site.site_header = "Keycard Pro Web"
admin.site.site_title = "Keycard Pro Web"
admin.site.index_title = "Admin"
