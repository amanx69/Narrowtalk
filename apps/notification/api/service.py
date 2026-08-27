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

    if not recipient:
        return None

    if sender and recipient.id == sender.id:
        return None

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


# --- Post Specific Notification Services ---

def notify_post_created(project):
    return notify.delay(
        recipient_id = project.owner.id,
        sender_id    = None,
        notif_type   = Notification.Type.POST_CREATED,
        title        = "Post Published",
        body         = f"Your post '{project.title}' is now published and active.",
        project_id   = project.id,
    )

def notify_post_updated(project):
    memberships = project.memberss.filter(is_active=True).exclude(user=project.owner)
    for membership in memberships:
        notify.delay(
            recipient_id = membership.user.id,
            sender_id    = project.owner.id,
            notif_type   = Notification.Type.POST_UPDATED,
            title        = "Post Updated",
            body         = f"The post '{project.title}' has been updated.",
            project_id   = project.id,
        )

def notify_new_role_added(role):
    project = role.project
    memberships = project.memberss.filter(is_active=True).exclude(user=project.owner)
    for membership in memberships:
        notify.delay(
            recipient_id = membership.user.id,
            sender_id    = project.owner.id,
            notif_type   = Notification.Type.NEW_ROLE_ADDED,
            title        = "New Role Added",
            body         = f"New role '{role.title}' was added to post '{project.title}'.",
            project_id   = project.id,
        )

def notify_application_received(application):
    applicant_name = get_user_name(application.user)
    notify.delay(
        recipient_id = application.role.project.owner.id,
        sender_id    = application.user.id,
        notif_type   = Notification.Type.APPLICATION_RECEIVED,
        title        = "New Application Received",
        body         = f"{applicant_name} applied for '{application.role.title}' in '{application.role.project.title}'.",
        project_id   = application.role.project.id,
    )

def notify_application_accepted(application):
    notify.delay(
        recipient_id = application.user.id,
        sender_id    = application.role.project.owner.id,
        notif_type   = Notification.Type.APPLICATION_ACCEPTED,
        title        = "Application Accepted!",
        body         = f"Congratulations! You were selected for '{application.role.title}' in '{application.role.project.title}'.",
        project_id   = application.role.project.id,
    )

def notify_application_rejected(application):
    notify.delay(
        recipient_id = application.user.id,
        sender_id    = application.role.project.owner.id,
        notif_type   = Notification.Type.APPLICATION_REJECTED,
        title        = "Application Status Update",
        body         = f"Your application for '{application.role.title}' in '{application.role.project.title}' was not selected.",
        project_id   = application.role.project.id,
    )

def notify_application_withdrawn(application):
    applicant_name = get_user_name(application.user)
    notify.delay(
        recipient_id = application.role.project.owner.id,
        sender_id    = application.user.id,
        notif_type   = Notification.Type.APPLICATION_WITHDRAWN,
        title        = "Application Withdrawn",
        body         = f"{applicant_name} withdrew their application for '{application.role.title}'.",
        project_id   = application.role.project.id,
    )

def notify_new_member(project, new_member):
    member_name = get_user_name(new_member)
    memberships = project.memberss.filter(is_active=True).exclude(user=new_member)
    for membership in memberships:
        notify.delay(
            recipient_id = membership.user.id,
            sender_id    = new_member.id,
            notif_type   = Notification.Type.NEW_MEMBER,
            title        = "New Team Member Joined",
            body         = f"{member_name} joined post '{project.title}'.",
            project_id   = project.id,
        )

def notify_member_left(project, member):
    member_name = get_user_name(member)
    notify.delay(
        recipient_id = project.owner.id,
        sender_id    = member.id,
        notif_type   = Notification.Type.MEMBER_LEFT,
        title        = "Member Left Team",
        body         = f"{member_name} has left post '{project.title}'.",
        project_id   = project.id,
    )

def notify_project_closed(project):
    memberships = project.memberss.filter(is_active=True)
    for membership in memberships:
        notify.delay(
            recipient_id = membership.user.id,
            sender_id    = project.owner.id,
            notif_type   = Notification.Type.PROJECT_CLOSED,
            title        = "Post Closed",
            body         = f"The post '{project.title}' has been closed.",
            project_id   = project.id,
        )



