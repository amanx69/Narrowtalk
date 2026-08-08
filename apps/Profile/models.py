from django.db import models
from django.contrib.auth import  get_user_model


User= get_user_model()


class Profile(models.Model):
    user=models.OneToOneField(User,models.CASCADE,related_name="user_profile")
    bio= models.CharField(max_length=100)
    profile_pic= models.ImageField(upload_to="profile/")
    choices_field=[
        ("Beginner","beginner"),
        ("Intermediate",'intermediate'),
        ("Advance","advance")
    ]
    english_lable=models.CharField(choices=choices_field,max_length=12)
    created_at= models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(null=True,blank=True)
    username= models.CharField(max_length=25,unique=True)
    
    
    def __str__(self):
        return self.username
    
    
    
    