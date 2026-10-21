from celery import shared_task
from ..service.feathures import increment_view_count
from django.contrib.auth import get_user_model
from apps.post.models import Project
from .serializer import FeedSerializer
from django.core.cache import cache


@shared_task
def increment_count(project_id, user):
    User = get_user_model()

    if not Project.objects.filter(id=project_id).exists():
        return
    if not User.objects.filter(id=user).exists():
        return

    increment_view_count(project_id, user) 

    






@shared_task
def recompute_best_ideas_cache():
    queryset = (
        Project.objects.filter(is_active=True, is_delete=False)
        .select_related('owner')
        .order_by('-like_count', '-application_count', '-view_count')[:10]
    )
    ser = FeedSerializer(queryset, many=True)
    cache.set('best_ideas_strip_v1', ser.data, timeout=600)