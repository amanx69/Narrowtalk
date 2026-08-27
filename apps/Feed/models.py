from django.db import models
from apps.post.models import Project
import uuid
from django.contrib.auth import get_user_model

User=get_user_model()


class ProjectLike(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    user= models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="user_like")
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="project_like")
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        unique_together = ['user','project']
        ordering=['created_at']
     
    
    

class Projectcomment(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    user= models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="user_comment")
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="project_comment")
    text=models.TextField(max_length=500,blank=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    


class Projectsave(models.Model):
    id= models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    user= models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="user_save")
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="project_save")
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        unique_together = ['user','project']
        

class ProjectView(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='project_views')
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='views')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], name='unique_project_view')
        ]
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user} viewed {self.project}"