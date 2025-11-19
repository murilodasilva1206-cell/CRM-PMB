from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'papel', 'ativo', 'is_staff', 'data_criacao')
    list_filter = ('papel', 'ativo', 'is_staff', 'is_superuser', 'data_criacao')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefone')
    ordering = ('-data_criacao',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações do CRM', {
            'fields': ('papel', 'telefone', 'ativo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações do CRM', {
            'fields': ('papel', 'telefone', 'ativo')
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
