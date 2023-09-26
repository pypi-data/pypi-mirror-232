"""Admin pages for the notices app."""
from django.contrib import admin

from .models import AcknowledgedNotice, Notice, TranslatedNoticeContent


# Unregistered because we only want these CRUD-ed through the Notice Admin
class TranslatedNoticeContentAdmin(admin.TabularInline):
    model = TranslatedNoticeContent


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    inlines = [TranslatedNoticeContentAdmin]
    list_display = ["name", "active", "launch_date"]
    search_fields = ["name"]


@admin.register(AcknowledgedNotice)
class AcknowledgedNoticeAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = ["user", "notice", "response_type"]
    search_fields = ["user__username", "response_type"]
