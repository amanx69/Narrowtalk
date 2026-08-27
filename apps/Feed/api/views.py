from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.post.models import Project
from ..service.feathures import *
from rest_framework.generics import CreateAPIView
from .serializer import CommentSerlizer
from django.db.models import F
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import transaction
from .task import increment_count
from.serializer import FeedSerializer ,HomeFeedSerializer,GetCommentSerializer
from django.core.cache import cache
from ..models import Projectcomment

class LikeProjectView(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='user', rate='30/m', block=True)) 
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        result=toggle_like(request.user,project)
        return Response(result,status=status.HTTP_200_OK)
        


class CommentProjectView(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='user', rate='10/m', block=True)) 
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        ser=CommentSerlizer(data=request.data,context={'request':request})
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            ser.save(project=project)
            Project.objects.filter(id=project.id).update(
                comment_count=F('comment_count')+1 
            )
        return Response({
                "message":f"comment done on {project.id}"
            },status.HTTP_201_CREATED)
        
    def get(self,request,project_id):
        comment_cache=cache.get(f'comment_{project_id}')
        if comment_cache:
            return Response(comment_cache)
        comments= Projectcomment.objects.filter(project=project_id).select_related('user').order_by('created_at')
        ser=GetCommentSerializer(comments,many=True)
        cache.set(f'comment_{project_id}',ser.data,timeout=300) #TODO remove the cache 
        return Response({"data":ser.data},status.HTTP_200_OK)
        #TODO write deleted comment 


class SaveProjectView(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='user', rate='30/m', block=True)) 
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        result=toggle_save(request.user,project)
        return Response(result,status=status.HTTP_200_OK)
    
    
    
class ProjectViewTrackView(APIView):
    
    permission_classes = [IsAuthenticated]
    def post(self, request,project_id):
        get_object_or_404(Project, id=project_id)
        increment_count.delay(project_id, request.user.id) 
        return Response(status=status.HTTP_202_ACCEPTED)
       



from core.pagination import FeedPegination,HomeFeedPegination
#! feed endpoint
class FeedView(APIView):
    def get(self,request):
        data= Project.objects.filter(is_active=True).select_related('owner').exclude(owner=request.user).order_by('created_at') #TODO change it later 
        paginator = FeedPegination()
        page = paginator.paginate_queryset(data, request)
        ser = FeedSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(ser.data)
      
            
            
            

#! home feed
class HomeFeedView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        cache_data=cache.get('home_feed_cache')
        if cache_data:
            return Response(cache_data)
        data=Project.objects.filter(is_active=True).select_related('owner').prefetch_related('roles__required_skills').order_by('created_at').reverse()  
        paginator = HomeFeedPegination()
        page=paginator.paginate_queryset(data,request)
        ser= HomeFeedSerializer(page,many=True,context={'request': request})  
        cache.set('home_feed_cache',ser.data,timeout=500)   
        return paginator.get_paginated_response(ser.data)
        
        
    

#! tranding project

class TrandingProjectView(APIView):
    def get(self,request):
        
        cache_data=cache.get('best_ideas_strip')
        if  cache_data  :
            return Response(cache_data,status.HTTP_200_OK)
        queryset = (
                Project.objects.filter(is_active=True)
                .select_related('owner')
                .order_by('-like_count', '-application_count', '-view_count')[:10]
            )
        data=FeedSerializer(queryset,many=True)
        cache.set('best_ideas_strip',data.data,timeout=600)
        return Response(data.data)
        
            
        
        