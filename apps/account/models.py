from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
import secrets
import random
from django.utils import timezone

class UserManage(BaseUserManager):
    
    def create_user(self,email,password=None,**extra):
        
        if not email:
            raise ValueError("email are required")
        email= self.normalize_email(email)
        user= self.model(email=email,**extra)
        user.set_password(password)
        user.save(using= self._db)
        return user
    
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault('is_verify',True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser,PermissionsMixin):
    
    id= models.UUIDField(primary_key=True, unique=True,editable=False,default=uuid.uuid4)
    email= models.EmailField(unique=True)
    is_staff= models.BooleanField(default=False)
    is_active= models.BooleanField(default=True)
    is_verify= models.BooleanField(default=False)
    in_project_count=models.PositiveIntegerField(default=0) 
    created_at= models.DateTimeField(auto_now_add=True)
    notifiction_enable=models.BooleanField(default=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects= UserManage()
    
    
    def __str__(self):
        return self.email

    @property
    def username(self):
        try:
            profile = getattr(self, "user_profile", None)
            if profile and profile.username:
                return profile.username
        except Exception:
            pass
        return self.email.split("@")[0] if self.email else ""
    
    class Meta:
        indexes=[
            models.Index(fields=['created_at']),
            models.Index(fields=['email'])
        ]
    
    

    
    
    
class Emailverifiction(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    id= models.UUIDField(primary_key=True, unique=True,editable=False,default=uuid.uuid4)
    otp=models.CharField(unique=True)
    purpose_= [
        ("RESETPASSWORD","resetpassword"),
        ("VERIFY","verify")
    ]
    purpose= models.CharField(choices=purpose_,null=False,blank=False)
    created_at= models.DateTimeField(auto_now_add=True)
    used_it=models.BooleanField(default=False)
    attempts=models.PositiveIntegerField(default=0)

    
    
    def is_expire(self):
        
        from django.utils import timezone
        return (timezone.now() - self.created_at).total_seconds() > 600
    
    
    def __str__(self):
        return f"{self.user.email} to {self.otp}"    
    
    
    
class PasswordResetToken(models.Model):
    id=models.UUIDField(primary_key=True,unique=True,editable=False,default=uuid.uuid4)
    user= models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_passord_token")
    token=models.CharField(max_length=64,unique=True)
    expires_at = models.DateTimeField()
    used_it = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at
    
    
    def __str__(self):
        return f"{self.user.email} of {self.token}"
    
    