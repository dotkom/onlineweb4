from django.contrib import admin

from .models import CommitteeUpdate

@admin.register(CommitteeUpdate)
class CommitteeUpdateAdmin(admin.ModelAdmin):
    model = CommitteeUpdate
    list_display = ["content", "created_at"]
    search_fields = ["content", "group__name_short"]
