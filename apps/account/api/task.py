from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from ..models import Emailverifiction 
import secrets
User= get_user_model()
from decouple import config

import hashlib
from ..models import Emailverifiction
from .service import gernate_otp

@shared_task
def send_verification_email(id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return
    otp = gernate_otp(user)

    context = {
        'username': user.username,
        'otp': otp
    }
    html_content = render_to_string('emails/verify_email.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Your Email Verification OTP",
        body=text_content,
        from_email="noreply@Narrow.com",
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()






@shared_task
def send_reset_password_email(id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return
    otp = gernate_otp(user)

    context = {
        'username': user.username,
        'otp': otp
    }
    html_content = render_to_string('emails/reset_password.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject="Password Reset OTP",
        body=text_content,
        from_email="noreply@Narrow.com",
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


 