# models.py
from django.db import models
from django.conf import settings
from apps.post.models import Project

class Notification(models.Model):
    class Type(models.TextChoices):
        # Post Application Events
        APPLICATION_RECEIVED  = "application_received",  "Application Received"
        APPLICATION_ACCEPTED  = "application_accepted",  "Application Accepted"
        APPLICATION_REJECTED  = "application_rejected",  "Application Rejected"
        APPLICATION_WITHDRAWN = "application_withdrawn", "Application Withdrawn"
        
        # Post / Role Management Events
        POST_CREATED          = "post_created",          "Post Created"
        POST_UPDATED          = "post_updated",          "Post Updated"
        NEW_ROLE_ADDED        = "new_role_added",        "New Role Added"
        PROJECT_CLOSED        = "project_closed",        "Post Closed"
        
        # Post Team Events
        NEW_MEMBER            = "new_member",            "New Member Joined"
        MEMBER_LEFT           = "member_left",           "Member Left"

    recipient  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    sender     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sent_notifications"
    )
    notif_type = models.CharField(max_length=30, choices=Type.choices)
    title      = models.CharField(max_length=100)
    body       = models.TextField()
    is_read    = models.BooleanField(default=False)
    project    = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.recipient} — {self.notif_type}"

    @property
    def post(self):
        return self.project
 