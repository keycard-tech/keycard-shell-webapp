from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("username", "email", "is_active", "is_superuser")
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("username", "email", "password", "is_superuser", "is_staff", "is_active")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "password1", "password2", "is_superuser", "is_staff",
                "is_active"
            )}
        ),
    )
    search_fields = ()
    ordering = ("email", "username")
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
      extra_context = extra_context or {}
      extra_context['subtitle'] = ""  
      
      return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)