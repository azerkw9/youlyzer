from django.contrib import admin
from .models import Ad, ContactMessage


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'created_at']
    list_filter = ['is_active', 'position']
    search_fields = ['title', 'text']
    list_editable = ['is_active']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'email', 'ip_address', 'sent_at', 'is_read']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['name', 'email', 'subject', 'message', 'ip_address']
    list_editable = ['is_read']
    readonly_fields = ['name', 'email', 'subject', 'message', 'ip_address', 'sent_at']
