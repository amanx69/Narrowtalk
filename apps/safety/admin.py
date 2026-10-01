from django.contrib import admin
from .models import UserBlock, Report

@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked_user', 'created_at')
    search_fields = ('blocker__email', 'blocked_user__email')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'get_target', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
    search_fields = ('reporter__email', 'description')
    
    # Custom column taki pata chale User report hua hai ya Project
    def get_target(self, obj):
        if obj.reported_user:
            return f"User: {obj.reported_user.email}"
        if obj.reported_project:
            return f"Project: {obj.reported_project.project_name}"
        return "Unknown"
    get_target.short_description = "Reported Target"