from django.db import models




class PostCustomManager(models.Manager):
    
    def is_active_Project(self):
        return self.filter(is_active=True)
    
    def Idea_project(self):
        return self.filter(stage='Idea')
    
    def Mvp_project(self):
        return self.filter(stage='MVP')
    
        
        
    
class ApplictionManager(models.Manager):
 
    def get_accpected_appliction(self):
        return self.filter(status='accepted')
        
    def get_rejected_appliction(self):
        return self.filter(status='rejected')
    
    def get_pending_appliction(self):
            return self.filter(status='pending')
        
    
    def get_appliction_status(self,s:str):
                return self.filter(status=s)
        
        
class ProjectManager(models.Manager):
    
    def current_user_project(self,user):
        return self.filter(user=user)