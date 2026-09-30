from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from core.permissions import Isowner 
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from apps.post.models import Project
from ..service.feathures import *
from rest_framework import generics
from .serializer import CommentSerlizer
from django.db.models import F
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import transaction
from rest_framework.generics import DestroyAPIView
from .task import increment_count
from.serializer import FeedSerializer ,HomeFeedSerializer,GetCommentSerializer ,ProjectSaveSerializer
from apps.post.api.serializers import ProjectSerializer
from ..models import Projectsave,Projectcomment,ProjectLike
from django.core.cache import cache
from core.throttling import *
from apps.safety.models import UserBlock 

class LikeProjectView(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='user', rate='30/m', block=True)) 
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        result=toggle_like(request.user,project)
        return Response(result,status=status.HTTP_200_OK)
        

#!  comment create and get current project comment
class CommentProjectView(APIView):
    permission_classes=[IsAuthenticated]
    
    
    def get_throttles(self):
        if self.request.method=='POST':
            return [commentCreatethrottle()]    
        return super().get_throttles()
    
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        if project.owner ==request.user:
            raise PermissionDenied("you don't comment own projecr")
        ser=CommentSerlizer(data=request.data,context={'request':request})
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            ser.save(project=project)
            Project.objects.filter(id=project.id).update(
                comment_count=F('comment_count')+1 
            )
        return Response({
                "message":"Comment posted successfully."
            },status.HTTP_201_CREATED)
        
    def get(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        comments= Projectcomment.objects.filter(project=project.id).select_related('user').order_by('created_at')
        ser=GetCommentSerializer(comments,many=True)
        return Response({"data":ser.data},status.HTTP_200_OK)
    
 #! delete comment
class DeleteComment(APIView):
    permission_classes=[IsAuthenticated,Isowner]
    throttle_classes=[commentDeletethrottle]
    def delete(self,request,project_id,comment_id):
        comment=get_object_or_404(Projectcomment,id=comment_id,project=project_id,user=request.user)
        comment.delete()
        return Response({"message": "Comment deleted successfully"},status.HTTP_200_OK)
        
    
    

class SaveProjectView(APIView):
    permission_classes=[IsAuthenticated]
    throttle_classes=[ProjectSaveThrottle]
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        result=toggle_save(request.user,project)
        return Response(result,status=status.HTTP_200_OK)


#! list of current user saveproject
class ProjectSaveListApiView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Projectsave.objects.filter(user=self.request.user)
    serializer_class=ProjectSaveSerializer
    
  
    
    
class ProjectViewTrackView(APIView):
    
    permission_classes = [IsAuthenticated]
    def post(self, request,project_id):
        get_object_or_404(Project, id=project_id)
        increment_count.delay(project_id, request.user.id) 
        return Response(status=status.HTTP_202_ACCEPTED)
       



from core.pagination import FeedPegination,HomeFeedPegination
#! feed endpoint
class FeedView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        blocked_by_me = UserBlock.objects.filter(blocker=request.user).values_list('blocked_user_id', flat=True)
        blocked_me = UserBlock.objects.filter(blocked_user=request.user).values_list('blocker_id', flat=True)
        blocked_users_ids = set(blocked_by_me).union(set(blocked_me))
        data= Project.objects.filter(is_active=True).select_related('owner').exclude(owner=request.user).exclude(owner_id__in=blocked_users_ids).order_by('created_at') 
        paginator = FeedPegination()
        page = paginator.paginate_queryset(data, request)
        ser = FeedSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(ser.data)
      
            
            
            

#! home feed
class HomeFeedView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        cache_data=cache.get(f'home_feed_cache_v2_{request.user.id}')
        if cache_data:
           pass
        blocked_by_me = UserBlock.objects.filter(blocker=request.user).values_list('blocked_user_id', flat=True)
        blocked_me = UserBlock.objects.filter(blocked_user=request.user).values_list('blocker_id', flat=True)
        blocked_users_ids = set(blocked_by_me).union(set(blocked_me))
        data=Project.objects.filter(is_active=True).select_related('owner').exclude(owner=request.user).exclude(owner_id__in=blocked_users_ids) .order_by('created_at') 
        paginator = HomeFeedPegination()
        page=paginator.paginate_queryset(data,request)
        ser= HomeFeedSerializer(page,many=True,context={'request': request})  
        response = paginator.get_paginated_response(ser.data)
        cache.set(f'home_feed_cache_v2_{request.user.id}', response.data, timeout=100)   
        return response
        
        
    

#! tranding project

class TrandingProjectView(APIView):
    def get(self,request):
        
        cache_data=cache.get('best_ideas_strip_v2')
        if  cache_data  :
            return Response(cache_data,status.HTTP_200_OK)
        queryset = (
                Project.objects.filter(is_active=True)
                .select_related('owner')
                .order_by('-like_count','-view_count')[:10]
            )
        data=FeedSerializer(queryset,many=True)
        cache.set('best_ideas_strip_v2',data.data,timeout=600)
        return Response(data.data)
        
            
        
        