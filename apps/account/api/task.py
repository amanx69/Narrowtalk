from django.core.mail import send_mail, EmailMultiAlternatives
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from ..models import Emailverifiction 
import secrets
User= get_user_model()
from decouple import config
from django.shortcuts import get_object_or_404
import hashlib
from ..models import Emailverifiction
from .service import gernate_otp

@shared_task
def send_verification_email(id):
    
    user= get_object_or_404(User,id=id)
    otp=gernate_otp(user)

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0; padding:0; background:#f4f6f8; font-family:Arial, sans-serif;">

    <div style="max-width:600px; margin:40px auto; background:#ffffff;
                border-radius:12px; padding:40px 30px;
                box-shadow:0 4px 15px rgba(0,0,0,0.08);">

        <h2 style="margin:0 0 15px; color:#222; text-align:center;">
            Verify Your Email
        </h2>

        <p style="color:#555; font-size:15px; line-height:1.6;">
            Hello <strong>{user.username}</strong>,
        </p>

        <p style="color:#555; font-size:15px; line-height:1.6;">
            Use the OTP below to verify your email address.
            This OTP is valid for <strong>10 minutes</strong>.
        </p>

        <div style="text-align:center; margin:30px 0;">
            <div style="display:inline-block; padding:15px 30px;
                        background:#f1f3f5; border-radius:10px;
                        font-size:32px; font-weight:bold;
                        letter-spacing:8px; color:#111;">
                {otp}
            </div>
        </div>

        <p style="color:#777; font-size:13px; line-height:1.5;">
            For your security, never share this OTP with anyone.
            If you did not request this code, you can safely ignore this email.
        </p>

        <hr style="border:0; border-top:1px solid #eee; margin:30px 0;">

        <p style="text-align:center; color:#999; font-size:12px;">
            © 2026 Narrow. All rights reserved.
        </p>

    </div>

</body>
</html>
"""

    msg = EmailMultiAlternatives(
        subject="Your Email Verification OTP",
        body=f"Your verification OTP is {otp}. It is valid for 10 minutes.",
        from_email="noreply@Narrow.com",
        to=[user.email],
     )

    msg.attach_alternative(html, "text/html")
    msg.send()






@shared_task
def send_reset_password_email(id):
    
    user= get_object_or_404(User,id=id)
    otp=gernate_otp(user)
   


    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0; padding:0; background:#f4f6f8;
             font-family:Arial, sans-serif;">

    <div style="max-width:600px; margin:40px auto;
                background:#ffffff; border-radius:12px;
                padding:40px 30px;
                box-shadow:0 4px 15px rgba(0,0,0,0.08);">

        <h2 style="margin:0 0 15px; color:#222; text-align:center;">
            Reset Your Password
        </h2>

        <p style="color:#555; font-size:15px; line-height:1.6;">
            Hello <strong>{user.username}</strong>,
        </p>

        <p style="color:#555; font-size:15px; line-height:1.6;">
            We received a request to reset your password.
            Use the OTP below to continue.
        </p>

        <div style="text-align:center; margin:30px 0;">
            <div style="display:inline-block;
                        padding:16px 28px;
                        background:#f1f3f5;
                        border-radius:10px;
                        font-size:32px;
                        font-weight:bold;
                        letter-spacing:8px;
                        color:#111;">
                {otp}
            </div>
        </div>

        <p style="color:#777; font-size:14px; text-align:center;">
            This OTP is valid for <strong>10 minutes</strong>.
        </p>

        <p style="color:#777; font-size:13px; line-height:1.5;">
            If you did not request a password reset, please ignore this
            email. Your password will not be changed.
        </p>

        <p style="color:#777; font-size:13px; line-height:1.5;">
            For your security, never share this OTP with anyone.
        </p>

        <hr style="border:0; border-top:1px solid #eee; margin:30px 0;">

        <p style="text-align:center; color:#999; font-size:12px;">
            © 2026 Narroe. All rights reserved.
        </p>

    </div>

</body>
</html>
"""

    msg = EmailMultiAlternatives(
        subject="Password Reset OTP",
        body=f"Your password reset OTP is {otp}. It is valid for 10 minutes.",
        from_email="noreply@Narrow.com",
        to=[user.email],
    )

    msg.attach_alternative(html, "text/html")
    msg.send()


 