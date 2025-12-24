"""
Abonent admin configuration - Zamonaviy admin panel.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Abonent, Inspektor


@admin.register(Abonent)
class AbonentAdmin(admin.ModelAdmin):
    """
    Abonent admin configuration with thumbnail preview and custom styling.
    """
    
    # List display
    list_display = [
        'id',
        'rasm_thumbnail',
        'abonent_kod',
        'toliq_ism_display',
        'pinfl',
        'jins',
        'telefon',
        'yaratilgan_vaqt',
    ]
    
    # List display links
    list_display_links = ['id', 'abonent_kod']
    
    # Search fields - abonent_kod, pinfl (JShShIR), ism, familiya
    search_fields = ['abonent_kod', 'pinfl', 'ism', 'familiya', 'telefon']
    
    # Filters
    list_filter = ['jins', 'yaratilgan_vaqt']
    
    # Ordering
    ordering = ['-id']
    
    # Pagination
    list_per_page = 20
    
    # Readonly fields for detail view - rasm preview
    readonly_fields = ['rasm_preview', 'yaratilgan_vaqt', 'yangilangan_vaqt']
    
    # Fieldsets for change form
    fieldsets = (
        ('Rasm', {
            'fields': ('rasm_preview', 'rasm'),
        }),
        ('Identifikatsiya', {
            'fields': ('abonent_kod', 'pinfl'),
        }),
        ('Pasport ma\'lumotlari', {
            'fields': ('pasport_seriya', 'pasport_raqam'),
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('familiya', 'ism', 'otasining_ismi', 'tugilgan_sana', 'jins'),
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('telefon', 'manzil'),
            'classes': ('collapse',),
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('yaratilgan_vaqt', 'yangilangan_vaqt'),
            'classes': ('collapse',),
        }),
    )
    
    # Add form fieldsets (without readonly fields)
    add_fieldsets = (
        ('Rasm', {
            'fields': ('rasm',),
        }),
        ('Identifikatsiya', {
            'fields': ('abonent_kod', 'pinfl'),
        }),
        ('Pasport ma\'lumotlari', {
            'fields': ('pasport_seriya', 'pasport_raqam'),
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('familiya', 'ism', 'otasining_ismi', 'tugilgan_sana', 'jins'),
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('telefon', 'manzil'),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """Add form uchun alohida fieldset."""
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    @admin.display(description='Rasm')
    def rasm_thumbnail(self, obj):
        """List display uchun thumbnail."""
        if obj.rasm:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" />',
                obj.rasm.url
            )
        return format_html(
            '<span style="color: #999; font-style: italic;">Rasm yo\'q</span>'
        )
    
    @admin.display(description='Rasm ko\'rinishi')
    def rasm_preview(self, obj):
        """Change form uchun katta rasm preview."""
        if obj.rasm:
            return format_html(
                '<img src="{}" width="200" height="200" '
                'style="object-fit: cover; border-radius: 10px; border: 2px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />',
                obj.rasm.url
            )
        return format_html(
            '<span style="color: #999; font-style: italic; font-size: 14px;">Rasm yuklanmagan</span>'
        )
    
    @admin.display(description='F.I.O')
    def toliq_ism_display(self, obj):
        """To'liq ismni ko'rsatish."""
        return obj.toliq_ism


@admin.register(Inspektor)
class InspektorAdmin(admin.ModelAdmin):
    """
    Inspektor admin configuration.
    """
    list_display = ['id', 'user', 'get_full_name', 'hudud', 'telefon', 'is_active', 'yaratilgan_vaqt']
    list_display_links = ['id', 'user']
    list_filter = ['is_active', 'hudud', 'yaratilgan_vaqt']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'hudud', 'telefon']
    ordering = ['-id']
    list_per_page = 20
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',),
        }),
        ('Inspektor ma\'lumotlari', {
            'fields': ('hudud', 'lavozim', 'telefon'),
        }),
        ('Holat', {
            'fields': ('is_active',),
        }),
    )
    
    @admin.display(description='F.I.O')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

