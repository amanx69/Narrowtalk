from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.post.models import Project
from .models import ChatGroup, GroupMember


@receiver(post_save, sender=Project)
def create_project_chatGroupe(sender, instance, created, **kwargs):
    if created:
        
        Chat_groupe= ChatGroup.objects.create(
            project=instance,
            group_name=instance.project_name
            
        )
        
        GroupMember.objects.create(
            chat_group=Chat_groupe,
            user=instance.owner,
            role=GroupMember.ChatRole.OWNER
        )
