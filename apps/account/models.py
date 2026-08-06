from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
import secrets


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
        return self.create_user(email, password, **extra_fields)





class User(AbstractBaseUser,PermissionsMixin):
    
    id= models.UUIDField(primary_key=True, unique=True,editable=False,default=uuid.uuid4)
    email= models.EmailField(unique=True)
    is_staff= models.BooleanField(default=False)
    is_active= models.BooleanField(default=True)
    is_verify= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects= UserManage()
    
    
    def __str__(self):
        return self.email
    
    

    
    
    
class Emailverifiction(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    id= models.UUIDField(primary_key=True, unique=True,editable=False,default=uuid.uuid4)
    token_hash= models.CharField(unique=True,) 
    purpose_= [
        ("RESETPASSWORD","resetpassword"),
        ("VERIFY","verify")
    ]
    purpose= models.CharField(choices=purpose_,null=False,blank=False)
    created_at= models.DateTimeField(auto_now_add=True)
    used_it=models.BooleanField(default=False)
    expire_at= models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.user.email} to {self.token_hash}"
    
    
    def is_expire(self):
        
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 3600 
    
    
    