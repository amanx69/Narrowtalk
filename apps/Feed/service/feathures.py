from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from apps.post.models import *
from..models import *




def toggle_like(user,project):
    like= ProjectLike.objects.filter(user=user,project=project).first()
    with transaction.atomic():
        if like:
            like.delete()
            Project.objects.filter(id=project.id).update(
                like_count=F('like_count') - 1
            )
            liked = False
        else:
            ProjectLike.objects.create(user=user,project=project)
            Project.objects.filter(id=project.id).update(
                        like_count=F('like_count') +1
                        )
            liked=True 
    project.refresh_from_db(fields=['like_count'])
    cache.delete(f'home_feed_cache_v2_{user.id}')
    return{"liked": liked, "like_count": project.like_count,"project_id":project.id}
            
        

def toggle_save(user,project):
    existing_save = Projectsave.objects.filter(user=user, project=project).first()
    with transaction.atomic():
        if existing_save:
            existing_save.delete()
            Project.objects.filter(id=project.id).update(
                save_count=F('save_count') - 1
            )
            saved = False
        else:
            Projectsave.objects.create(user=user, project=project)
            Project.objects.filter(id=project.id).update(
                save_count=F('save_count') + 1
            )
            saved = True
    project.refresh_from_db(fields=['save_count'])
    cache.delete(f'home_feed_cache_v2_{user.id}')
    return {"saved": saved, "save_count": project.save_count,"project_id":project.id}
    
    

#! incremant the view
def increment_view_count(project_id,user_id):
    _,created=ProjectView.objects.get_or_create(project=project_id,user=user_id)

    if created:
        with transaction.atomic():
            project=Project.objects.filter(id=project_id).update(
                view_count=F('view_count') + 1
            )
    
            project.refresh_from_db(fields=['view_count'])
    
        
    