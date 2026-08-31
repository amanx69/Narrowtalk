# service.py
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import Notification
from celery import shared_task

def get_user_name(user):
    if not user:
        return "System"
    try:
        profile = getattr(user, "user_profile", None)
        if profile and profile.username:
            return profile.username
    except Exception:
        pass
    if hasattr(user, "username") and user.username:
        return user.username
    return user.email.split("@")[0] if hasattr(user, "email") and user.email else "User"

@shared_task
def notify(recipient_id, sender_id, notif_type, title, body, project_id=None):
    from django.contrib.auth import get_user_model
    from apps.post.models import Project

    User = get_user_model()
    recipient = User.objects.filter(id=recipient_id).first()
    sender = User.objects.filter(id=sender_id).first() if sender_id else None
    project = Project.objects.filter(id=project_id).first() if project_id else None
    print(recipient.id)
    print(recipient.notifiction_enable)

    if not recipient:
        return None

    if sender and recipient.id == sender.id:
        return None
    
    if  recipient.notifiction_enable:
      

        notification = Notification.objects.create(
            recipient  = recipient,
            sender     = sender,
            notif_type = notif_type,
            title      = title,
            body       = body,
            project    = project,
        )

        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{recipient.id}",
                    {
                        "type":        "send_notification",
                        "id":          str(notification.id),
                        "notif_type":  notif_type,
                        "title":       title,
                        "body":        body,
                        "project_id":  str(project.id) if project else None,
                        "post_id":     str(project.id) if project else None,
                        "sender_name": get_user_name(sender),
                        "is_read":     False,
                        "created_at":  notification.created_at.isoformat(),
                    }
                )
        except Exception as e:
            print(f"WebSocket notification error: {e}")

        return str(notification.id)




def notify_application_received(application):
    applicant_name = get_user_name(application.user)
    notify.delay(
        recipient_id = application.role.project.owner.id,
        sender_id    = application.user.id,
        notif_type   = Notification.Type.APPLICATION_RECEIVED,
        title        = "New Application Received",
        body         = f"{applicant_name} applied for '{application.role.project.project_name}'.",
        project_id   = application.role.project.id,
    )

def notify_application_accepted(application):
    notify.delay(
        recipient_id = application.user.id,
        sender_id    = application.role.project.owner.id,
        notif_type   = Notification.Type.APPLICATION_ACCEPTED,
        title        = "Application Accepted!",
        body         = f"Congratulations! You were selected for '{application.role.project.project_name}'.",
        project_id   = application.role.project.id,
    )

def notify_application_rejected(application):
    notify.delay(
        recipient_id = application.user.id,
        sender_id    = application.role.project.owner.id,
        notif_type   = Notification.Type.APPLICATION_REJECTED,
        title        = "Application Status Update",
        body         = f"Your application for '{application.role.project.project_name}' was not selected.",
        project_id   = application.role.project.id,
    )

def notify_application_withdrawn(application):
    applicant_name = get_user_name(application.user)
    notify.delay(
        recipient_id = application.role.project.owner.id,
        sender_id    = application.user.id,
        notif_type   = Notification.Type.APPLICATION_WITHDRAWN,
        title        = "Application Withdrawn",
        body         = f"{applicant_name} withdrew their application for '{application.role.project.project_name}'.",
        project_id   = application.role.project.id,
    )

def notify_new_member(recipient_id, member_user, project):
    member_name = get_user_name(member_user)
    notify.delay(
        recipient_id = recipient_id,
        sender_id    = member_user.id,
        notif_type   = Notification.Type.NEW_MEMBER,
        title        = "New Member Joined",
        body         = f"{member_name} joined '{project.project_name}'.",
        project_id   = project.id,
    )

def notify_member_left(recipient_id, member_user, project):
    member_name = get_user_name(member_user)
    notify.delay(
        recipient_id = recipient_id,
        sender_id    = member_user.id,
        notif_type   = Notification.Type.MEMBER_LEFT,
        title        = "Member Left",
        body         = f"{member_name} left '{project.project_name}'.",
        project_id   = project.id,
    )


