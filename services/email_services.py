from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from celery import shared_task
from apps.post.models import Application
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User=get_user_model()


#! accpect appliction  mail
@shared_task
def AccpectedAppliction_email(appliction_id):
    
    try:
        appliction= Application.objects.get(id=appliction_id)
        
        context = {
            "username":appliction.user.username,
            "role":appliction.role.title,
            "project":appliction.role.project.project_name
            
        }
        html_content = render_to_string('emails/application_accepted.html', context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
                subject=f"Application update",
                body=text_content,
                from_email=None,
                to=[appliction.user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
        
    except Application.DoesNotExist:
        return

    
 
#! remove project mail 
@shared_task
def RemoveProjectMail(user_id, project_name):
    
    try:
        user = User.objects.get(id=user_id)
        
        context = {
            'username': user.username,
            'project_name': project_name,
        }

        html_content = render_to_string('emails/member_removed.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=f"Project Update: {project_name}",
            body=text_content,
            from_email=None,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
    except User.DoesNotExist:
        pass

@shared_task
def MemberLeftProjectMail(owner_id, leaving_user_id, project_name, role_title=None):
    try:
        owner = User.objects.get(id=owner_id)
        leaving_user = User.objects.get(id=leaving_user_id)
        
        context = {
            'owner_username': owner.username,
            'leaving_username': leaving_user.username,
            'project_name': project_name,
            'role_title': role_title,
        }

        html_content = render_to_string('emails/member_left_project.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=f"Project Update: Someone left {project_name}",
            body=text_content,
            from_email=None,
            to=[owner.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
    except User.DoesNotExist:
        pass
@shared_task
def NewApplicationReceivedMail(application_id):
    try:
        app = Application.objects.get(id=application_id)
        owner = app.role.project.owner
        applicant = app.user
        
        context = {
            'owner_username': owner.username,
            'applicant_username': applicant.username,
            'project_name': app.role.project.project_name,
            'role_title': app.role.title,
            'message': app.message,
        }

        html_content = render_to_string('emails/new_application_received.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=f"New Application for {app.role.title} in {app.role.project.project_name}",
            body=text_content,
            from_email=None,
            to=[owner.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
    except Application.DoesNotExist:
        pass
