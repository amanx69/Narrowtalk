from ..models import Emailverifiction ,PasswordResetToken
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone

#! gernate a otp
def gernate_otp(user):
    Emailverifiction.objects.filter(user=user).delete()
    otp= str(secrets.randbelow(900000) + 100000)
    hash_otp= hashlib.sha256(otp.encode()).hexdigest()
    Emailverifiction.objects.create(
        user=user,
        otp=hash_otp
            
        )
    return otp
        

def gernate_password_token(user):
    token= secrets.token_urlsafe(32)
    token_hash=hashlib.sha256(token.encode()).hexdigest()
    PasswordResetToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(minutes=10),
        token=token_hash,
    )
    return token 