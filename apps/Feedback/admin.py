from django.contrib import admin
from .models import AppFeedback

@admin.register(AppFeedback)
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_type', 'title', 'status', 'created_at')
    list_filter = ('feedback_type', 'status', 'created_at')
    search_fields = ('title', 'description', 'user__email')
