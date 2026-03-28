from django.contrib import admin

from .models import ExtractionMethod, PANForm49A, VoterIDForm6


@admin.register(ExtractionMethod)
class ExtractionMethodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'provider',
        'is_visible',
        'is_enabled',
        'supports_checkboxes',
        'requires_api_key',
        'sort_order',
    )
    list_filter = ('provider', 'is_visible', 'is_enabled', 'supports_checkboxes', 'requires_api_key')
    search_fields = ('name', 'slug', 'provider', 'description')
    ordering = ('sort_order', 'name')


@admin.register(PANForm49A)
class PANForm49AAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_on_card', 'status', 'extraction_method', 'created_at')
    list_filter = ('status', 'extraction_method', 'created_at')
    search_fields = ('name_on_card', 'aadhaar_number', 'phone_number', 'email_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VoterIDForm6)
class VoterIDForm6Admin(admin.ModelAdmin):
    list_display = ('id', 'name_english', 'status', 'extraction_method', 'created_at')
    list_filter = ('status', 'extraction_method', 'created_at')
    search_fields = ('name_english', 'name_hindi', 'aadhaar_number', 'mobile_number', 'email_id')
    readonly_fields = ('created_at', 'updated_at')
