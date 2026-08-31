from django.db import models
from django.contrib.auth import  get_user_model
import uuid


User= get_user_model()


class Skill(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    name = models.CharField(max_length=60,)
    created_at=models.DateTimeField(auto_now_add=True)
  
 
 
 
    def __str__(self):
        return self.name
 
class Profile(models.Model):
    class stage(models.TextChoices):
        OPEN_TO_JOIN = "open_to_join", "Open to Join"
        SELECTIVELY_AVAILABLE = "selectively_available", "Selectively Available"
        NOT_AVAILABLE = "not_available", "Not Available"
        LOOKING_FOR_TEAM = "looking_for_team", "Looking for a Team"
    class Role(models.TextChoices):
        FOUNDER = "founder", "Founder"
        DEVELOPER = "developer", "Developer"
        DESIGNER = "designer", "Designer"
        PRODUCT = "product", "Product"
        MARKETING = "marketing", "Marketing"
        

    id=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4,unique=True)
    user=models.OneToOneField(User,models.CASCADE,related_name="user_profile")
    avter_image=models.ImageField(upload_to="avter/",null=True)
    bio= models.CharField(max_length=300,default="") 
    profile_pic= models.ImageField(upload_to="profile/")
    created_at= models.DateTimeField(auto_now_add=True)
    username= models.CharField(max_length=25,default="") 
    role=models.CharField(max_length=50,choices=Role.choices,default=Role.DEVELOPER)
    links = models.JSONField(default=dict, blank=True)
    skills=models.ManyToManyField(Skill,related_name="Profiles", blank=True)
    availability=models.CharField(max_length=50,choices=stage.choices,default=stage.OPEN_TO_JOIN)
    project_joined=models.PositiveIntegerField(default=0)
    project_completed=models.PositiveIntegerField(default=0)
    looking_for=models.CharField(max_length=150,null=True,blank=True)
    profile_like=models.PositiveIntegerField(default=0)
    
    
    
    
    def __str__(self):
        return self.username
    
    
    
 
class ProfileLIke(models.Model):
    
    user=models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='user_profile_like')
    profile=models.ForeignKey(Profile,on_delete=models.DO_NOTHING,related_name="profile_likes")
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        unique_together=['user','profile']
        
        
    def __str__(self) -> str:
        return f'{self.user.email} like {self.profile.username}' 
        
    
    
     
