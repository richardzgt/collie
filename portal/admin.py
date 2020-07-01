from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Quota'), {'fields': ('quota', 'expire_date')}),
        (_('Personal info'), {'fields': ('company',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'company', 'password1', 'password2'),
        }),
    )
    list_display = ('company', 'email', 'username', 'is_staff')
    search_fields = ('company', 'username', 'email')
    ordering = ('company', 'expire_date')
