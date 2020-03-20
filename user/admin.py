from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Kraj, Okres, Skola, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_per_page = 100

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff'
    )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups'
    )

    search_fields = [
        'first_name',
        'last_name',
        'email',
        'school',
    ]
    ordering = ('last_name', 'first_name')

    # filter_horizontal = ['groups', 'user_permissions']
    readonly_fields = ('last_login',)

    fieldsets = (
        ('Prihlásenie', {
            'classes': ('wide',),
            'fields': ('email', 'email_verified', 'password', 'last_login'),
        }),
        ('Osoba', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'school', ('phone', 'parent_phone')),
        }),
        ('Oprávnenia', {
            'classes': ('wide',),
            'fields': (('is_staff', 'is_superuser'), 'groups'),
        }),
        ('Extra oprávnenia', {
            'classes': ('collapse',),
            'fields': ('user_permissions',),
            'description': 'Za normálnych okolností sa neudeľujú a mali by vystačiť ' +
            'skupiny oprávnení, avšak pre nejaké špeciálne potreby môžu byť ' +
            'využité. Priraďujú oprávnenia nad rámec skupín.'
        }),
    )

    add_fieldsets = (
        ('Prihlásenie', {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'),
        }),
        ('Osoba', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'school', ('phone', 'parent_phone')),
        }),
        ('Oprávnenia', {
            'classes': ('wide',),
            'fields': (('is_staff', 'is_superuser'), 'groups'),
        }),
    )


admin.site.register(Permission)
admin.site.register(Kraj)
admin.site.register(Okres)
admin.site.register(Skola)
