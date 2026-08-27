from django.core.mail import send_mail, EmailMultiAlternatives
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from ..models import Emailverifiction 
import secrets
User= get_user_model()
              

@shared_task
def send_verification_email(id):
    
    user= User.objects.get(id=id)
    token=  secrets.token_urlsafe(32)
    purose="VERIFY"

    email= Emailverifiction.objects.create(
        user=user,
        token_hash=token,
        purpose=purose
    )
    
    link = f"http://localhost:8000/api/v1/auth/verify-email/{email.token_hash}/"

#TODO make beautiful  and readable
    html = f"""
    <h2>Verify your email</h2>
    <p>Click below:</p>
    <a href="{link}"> ClickVerify Email</a>
    """

    msg = EmailMultiAlternatives(
        "Verify your email",
        "Click link to verify",
        "noreply@yourapp.com",
        [user.email]
    )
    msg.attach_alternative(html, "text/html")
    msg.send()

@shared_task
def send_reset_password_email(id):
    
    user= User.objects.get(id=id)
    token=  secrets.token_urlsafe(32)
    purose="RESETPASSWORD"
    email= Emailverifiction.objects.create(
        user=user,
        token_hash=token,
        purpose=purose
    )
    
    link = f"http://localhost:8000/api/v1/auth/reset-password/{email.token_hash}/"

#TODO make beautiful  and readable
    html = f"""
    <h2>Reset your password</h2>
    <p>Click below:</p>
    <a href="{link}"> ClickReset Password</a>
    """

    msg = EmailMultiAlternatives(
        "Reset your password",
        "Click link to reset your password",
        "noreply@yourapp.com",
        [user.email]
    )
    msg.attach_alternative(html, "text/html")
    msg.send()
