import logging
from celery import shared_task
from apps.Profile.models import Profile
from django.db.models import F

def _safe_notify(func, *args, **kwargs):

    try:
        func(*args, **kwargs)
    except Exception as exc:   
        return        
      
#! this function update project join field in profile
@shared_task
def Update_profile_project_join(profile_id):
    Profile.objects.filter(id=profile_id).update( 
            project_joined=F('project_joined')+1
                )
    

    
@shared_task
def decrement_profile_project_join(profile_id):
    Profile.objects.filter(id=profile_id).update( 
            project_joined=F('project_joined')-1
                )
     
     
#! increment and decrement project create count


def Increment_Project_Create_Count(profile_id):
    Profile.objects.filter(id=profile_id).update(
        project_count=F('project_count')+1
        
    )
    
    
def Decrement_Project_Create_Count(profile_id):
    Profile.objects.filter(id=profile_id).update(
        project_count=F('project_count')-1
        
    )