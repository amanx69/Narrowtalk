from django.db import models
from django.contrib.auth import get_user_model
from apps.post.models import Project
import uuid

User = get_user_model()

# 1. Block System
class UserBlock(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    # Jisko block kiya gaya hai
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['blocker', 'blocked_user']
        indexes = [
            models.Index(fields=['blocked_user', 'blocker']),
            models.Index(fields=['blocker', 'created_at']),
        ]

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked_user.email}"



class Report(models.Model):
    class ReportReason(models.TextChoices):
        # Universal / General
        SPAM = "spam", "Spam or Scam"
        INAPPROPRIATE = "inappropriate", "Inappropriate Content"
        HARASSMENT = "harassment", "Harassment or Bullying"
        OTHER = "other", "Other"

        # User-specific
        FAKE_PROFILE = "fake_profile", "Fake Profile or Impersonation"
        HATE_SPEECH = "hate_speech", "Hate Speech or Hostility"

        # Group-specific
        MISLEADING_GROUP = "misleading_group", "Misleading or Fraudulent Group"
        ABUSIVE_CHAT = "abusive_chat", "Abusive or Toxic Messages"
        VIOLENCE = "violence", "Violence or Dangerous Activities"

        # Project-specific
        FAKE_PROJECT = "fake_project", "Fake or Scam Project"
        COPYRIGHT = "copyright", "Plagiarism or IP Infringement"

    class ReportStatus(models.TextChoices):
        PENDING = "pending", "Pending Review"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_submitted')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received', null=True, blank=True)
    reported_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reported_group = models.ForeignKey('Chats.ChatGroup', on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reason = models.CharField(max_length=50, choices=ReportReason.choices)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reporter', '-created_at']),
        ]

    def __str__(self):
        if self.reported_user:
            target = self.reported_user.email
        elif self.reported_project:
            target = self.reported_project.project_name
        elif self.reported_group:
            target = f"Group: {self.reported_group.group_name}"
        else:
            target = "Unknown"
        return f"Report by {self.reporter.email} on {target} ({self.status})"