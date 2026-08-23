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

class LikeProjectView(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='user', rate='30/m', block=True)) 
    def post(self,request,project_id):
        project=Project.objects.get(id=project_id)
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
        


class SaveProjectView(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='user', rate='30/m', block=True)) 
    def post(self,request,project_id):
        project=get_object_or_404(Project,id=project_id)
        result=toggle_save(request.user,project)
        return Response(result,status=status.HTTP_200_OK)
    
    
    
class ProjectViewTrackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        get_object_or_404(Project, id=project_id)  
        increment_count.delay(project_id) 
        return Response(status=status.HTTP_202_ACCEPTED)



#TODO MAKE feed endpoint




#TODO learn and  make recommendtion for user


#TODO show data in home page