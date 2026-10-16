from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "phone_display", "status", "utm_source", "notified")
    list_filter = ("status", "notified", "utm_source", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "phone", "message")
    readonly_fields = ("created_at", "ip_address", "notified")
    date_hierarchy = "created_at"

    @admin.display(description="Телефон")
    def phone_display(self, obj: Lead) -> str:
        return obj.phone_display
