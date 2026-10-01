import uuid
from django.db import models
from django.contrib.auth import get_user_model
from core.storage import AutoMediaCloudinaryStorage # Cloudinary ke liye

User = get_user_model()

class AppFeedback(models.Model):
  
    class FeedbackType(models.TextChoices):
        BUG = "bug", "Bug Report"
        FEATURE = "feature", "Feature Request"
        GENERAL = "general", "General Feedback"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Under Review"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    feedback_type = models.CharField(max_length=20, choices=FeedbackType.choices, default=FeedbackType.GENERAL)
    title = models.CharField(max_length=255, help_text="Short summary of the feedback")
    description = models.TextField(help_text="Detailed explanation")
    
    attachment = models.FileField(upload_to="feedbacks/screenshots/", storage=AutoMediaCloudinaryStorage(), null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "App Feedback"
        verbose_name_plural = "App Feedbacks"

    def __str__(self):
        return f"{self.get_feedback_type_display()} from {self.user.username} ({self.status})"