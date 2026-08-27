from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

from django.db import models
from django.conf import settings
from apps.Profile.models import Skill  
import uuid
from core.ModelsManager import ApplictionManager,PostCustomManager





class Project(models.Model):
    class Stage(models.TextChoices):
        IDEA = "idea", "Idea"
        MVP = "mvp", "MVP"
        FUNDED = "funded", "Funded"
        SCALING = "scaling", "Scaling"
        PROJECT= 'proejct','Project'
        COLLAGE_PROJECT="collage_project","Collage_Project"
        Learning_Project='learning_project','Learning_project'
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects_owner"
    )
    title = models.CharField(max_length=150)
    
    description = models.TextField()
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.IDEA)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    links = models.JSONField(default=dict, blank=True)  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_delete=models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    save_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0) 
    file = models.FileField(null=True,blank=True,upload_to="ProjectFile/",name="project_file")
    
    #TODO add filefield or image field show poject detiles via pdf or video

    custom_manager=PostCustomManager()
    objects = models.Manager() 
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class RoleNeeded(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="roles")
    title = models.CharField(max_length=100)  
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill, related_name="roles_req", blank=True)
    slots_available = models.PositiveIntegerField(default=1)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role=models.TextField(max_length=40,blank=True)
    is_complete= models.BooleanField(default=False)
    appliction_count=models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.title} @ {self.project.title}"





class Application(models.Model):

    
    class purpose(models.TextChoices):
            BACKEND = "backend", "BACKEND"
            FRONTEND= "frontend", "FRONTEND"
            FULLSTACK="fullstack","FULLSTACK"
            AIML= "ai/ml", "AI/ML" 
            OTHER="other","OTHER"
    
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"  
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    role = models.ForeignKey(RoleNeeded, on_delete=models.CASCADE, related_name="applications")
    apply_role_purpose=models.CharField(choices=purpose.choices,max_length=30,blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    github_link=models.URLField(null=True,blank=True,max_length=300)
    portfolio_link=models.URLField(null=True,blank=True,max_length=300)
    
    
    custom_objects=ApplictionManager()
    objects = models.Manager() 
    class Meta:
        unique_together = ("user", "role") 
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.role} ({self.status})"
    
    


class Membership(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="memberships"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberss")
    role_title = models.CharField(max_length=100, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:  
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user} in {self.project} as {self.role_title}"
    
    
    
    
    
    