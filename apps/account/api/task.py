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
    print(token)
    email= Emailverifiction.objects.create(
        user=user,
        token_hash=token
    )
    
    link = f"http://localhost:8000/api/auth/verify-email/{email.token_hash}/"
    print(link)

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
