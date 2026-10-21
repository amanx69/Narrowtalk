from django.db import models
from django.contrib.auth import get_user_model
from apps.post.models import Project
import uuid
from core.storage import AutoMediaCloudinaryStorage

User = get_user_model()

class ChatGroup(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="chat_group")
    group_name = models.CharField(max_length=100)
    group_dp = models.ImageField(upload_to="chats/group_dps/", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name


class GroupMember(models.Model):
    class ChatRole(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        OWNER = "owner", "Owner" 

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_groups")
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ChatRole.choices, default=ChatRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['chat_group', 'user']
        indexes = [
            models.Index(fields=['chat_group', 'user', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.chat_group.group_name}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chats/files/", blank=True, null=True, storage=AutoMediaCloudinaryStorage())
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['group', 'created_at']),
        ]

    def __str__(self):
        return f"Message by {self.sender.email} in {self.group.group_name}"


class MessageReaction(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_reactions")
    emoji = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['message', 'emoji']),
            models.Index(fields=['message', 'user']),
        ]

    def __str__(self):
        return f"{self.user} reacted {self.emoji} on {self.message_id}"


from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Message)
def cleanup_message_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception:
            pass


@receiver(post_delete, sender=ChatGroup)
def cleanup_group_dp_on_delete(sender, instance, **kwargs):
    if instance.group_dp:
        try:
            instance.group_dp.delete(save=False)
        except Exception:
            pass