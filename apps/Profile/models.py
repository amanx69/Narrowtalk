from django.db import models
from django.contrib.auth import  get_user_model
import uuid


User= get_user_model()


class Skill(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    name = models.CharField(max_length=60,)
    category = models.CharField(max_length=60)
    is_custom = models.BooleanField(default=False)  
 
    class Meta:
        ordering = ["category", "name"]
        unique_together = ("name", "category") 
 
    def __str__(self):
        return self.name
 
class Profile(models.Model):
    #TODO add id in uuids
    user=models.OneToOneField(User,models.CASCADE,related_name="user_profile")
    avter_image=models.ImageField(upload_to="avter/",null=True)
    bio= models.CharField(max_length=100,default="") #TODO set defult ""
    profile_pic= models.ImageField(upload_to="profile/")
    choices_field=[
        ("Beginner","beginner"),
        ("Intermediate",'intermediate'), #TODO remove it later
        ("Advance","advance")
    ]
    english_lable=models.CharField(choices=choices_field,max_length=12,default="Beginner") #TODO set defult beginner
    created_at= models.DateTimeField(auto_now_add=True)
    username= models.CharField(max_length=25,default="") 
    links = models.JSONField(default=dict, blank=True)
    skills=models.ManyToManyField(Skill,related_name="Profiles", blank=True)
    
    
    
    
    def __str__(self):
        return self.username
    
    
    
 
