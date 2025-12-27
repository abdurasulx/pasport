"""
Abonent admin configuration - Zamonaviy admin panel.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Abonent, Inspektor, Tuman, Mahalla


@admin.register(Abonent)
class AbonentAdmin(admin.ModelAdmin):
    """
    Abonent admin configuration - simplified.
    """
    
    list_display = [
        'id',
        'rasm_thumbnail',
        'pinfl',
        'tuman',
        'mahalla',
        'inspektor',
        'yaratilgan_vaqt',
    ]
    
    list_display_links = ['id', 'pinfl']
    search_fields = ['pinfl', 'abonent_kod']
    list_filter = ['tuman', 'mahalla', 'inspektor', 'yaratilgan_vaqt']
    ordering = ['-id']
    list_per_page = 20
    readonly_fields = ['rasm_preview', 'yaratilgan_vaqt', 'yangilangan_vaqt']
    
    fieldsets = (
        ('Rasm', {
            'fields': ('rasm_preview', 'rasm'),
        }),
        ('Identifikatsiya', {
            'fields': ('abonent_kod', 'pinfl'),
        }),
        ('Hudud', {
            'fields': ('tuman', 'mahalla'),
        }),
        ('Tizim', {
            'fields': ('yaratilgan_vaqt', 'yangilangan_vaqt'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        ('Rasm', {
            'fields': ('rasm',),
        }),
        ('Identifikatsiya', {
            'fields': ('abonent_kod', 'pinfl'),
        }),
        ('Hudud', {
            'fields': ('tuman', 'mahalla'),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    @admin.display(description='Rasm')
    def rasm_thumbnail(self, obj):
        if obj.rasm:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" />',
                obj.rasm.url
            )
        return format_html('<span style="color: #999;">-</span>')
    
    @admin.display(description='Rasm')
    def rasm_preview(self, obj):
        if obj.rasm:
            return format_html(
                '<img src="{}" width="200" height="200" '
                'style="object-fit: cover; border-radius: 10px;" />',
                obj.rasm.url
            )
        return format_html('<span style="color: #999;">Rasm yuklanmagan</span>')


@admin.register(Tuman)
class TumanAdmin(admin.ModelAdmin):
    """
    Tuman (District) admin configuration.
    """
    list_display = ['id', 'nomi', 'mahallalar_soni', 'yaratilgan_vaqt']
    list_display_links = ['id', 'nomi']
    search_fields = ['nomi']
    ordering = ['nomi']
    list_per_page = 20
    
    @admin.display(description='Mahallalar soni')
    def mahallalar_soni(self, obj):
        return obj.mahallalar.count()


@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    """
    Mahalla (Neighborhood) admin configuration.
    """
    list_display = ['id', 'nomi', 'tuman', 'yaratilgan_vaqt']
    list_display_links = ['id', 'nomi']
    list_filter = ['tuman']
    search_fields = ['nomi', 'tuman__nomi']
    ordering = ['tuman', 'nomi']
    list_per_page = 20


@admin.register(Inspektor)
class InspektorAdmin(admin.ModelAdmin):
    """
    Inspektor admin configuration.
    """
    list_display = ['id', 'user', 'get_full_name', 'tuman', 'get_mahallalar', 'telefon', 'is_active', 'yaratilgan_vaqt']
    list_display_links = ['id', 'user']
    list_filter = ['is_active', 'tuman', 'yaratilgan_vaqt']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'tuman__nomi', 'telefon']
    ordering = ['-id']
    list_per_page = 20
    filter_horizontal = ['mahallalar']
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',),
        }),
        ('Hudud', {
            'fields': ('tuman', 'mahallalar'),
        }),
        ('Inspektor', {
            'fields': ('lavozim', 'telefon'),
        }),
        ('Holat', {
            'fields': ('is_active',),
        }),
    )
    
    @admin.display(description='F.I.O')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    @admin.display(description='Mahallalar')
    def get_mahallalar(self, obj):
        mahallalar = obj.mahallalar.all()[:3]
        names = [m.nomi for m in mahallalar]
        if obj.mahallalar.count() > 3:
            names.append(f"...+{obj.mahallalar.count() - 3}")
        return ", ".join(names) if names else "-"
