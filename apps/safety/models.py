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

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked_user.email}"



class Report(models.Model):
    class ReportReason(models.TextChoices):
        SPAM = "spam", "Spam or Scam"
        INAPPROPRIATE = "inappropriate", "Inappropriate Content"
        HARASSMENT = "harassment", "Harassment or Bullying"
        FAKE_PROFILE = "fake_profile", "Fake Profile"
        OTHER = "other", "Other"

    class ReportStatus(models.TextChoices):
        PENDING = "pending", "Pending Review"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_submitted')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received', null=True, blank=True)
    reported_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reason = models.CharField(max_length=50, choices=ReportReason.choices)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.reported_user.email if self.reported_user else self.reported_project.project_name
        return f"Report by {self.reporter.email} on {target} ({self.status})"