from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action 
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
import datetime
from django.db import transaction
from django.utils.decorators import method_decorator
from django.db.models import F
from django.core.cache import cache
from ..models import Project, Membership, RoleNeeded, Application
from .serializers import (
    ProjectSerializer, 
    GetJobRoleSerializer, 
    CreateJobRoleSerializer,
    ApplictionSerializer,
    MemebrSerializer,
    GetapplictionSerializar,
    AppliedApplictionSerializer,
    
    
    )
from core.permissions import IsOwnerOrReadOnly,Isowner,IsProjectOwner ,IsProjectMember
from .service import _safe_notify
from apps.notification.api.service import (
    notify_post_created,
    notify_post_updated,
    notify_new_role_added,
    notify_application_received,
    notify_application_accepted,
    notify_application_rejected,
    notify_application_withdrawn,
    notify_new_member,
    notify_member_left,
    notify_project_closed,
)

class ProjectView(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = ProjectSerializer
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user,is_active=True)

    @method_decorator(ratelimit(key='user', rate='15/m', method='POST',block=True),)
    def perform_create(self, serializer):
            project = serializer.save(owner=self.request.user)
            _safe_notify(notify_post_created, project)

    @method_decorator(ratelimit(key='user', rate='5/m', method='PATCH',block=True),)
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        instance.updated_at=datetime.datetime.now()
        project = ser.save()
        _safe_notify(notify_post_updated, project)
        return Response(ser.data)

    def perform_destroy(self, instance, *args, **kwargs):
        _safe_notify(notify_project_closed, instance)
        instance.is_active = False
        instance.is_delete=True
        instance.save(update_fields=["is_active",'is_delete'])

    @action(detail=True, methods=["get", "post"], url_path="create_job_role")
    @method_decorator(ratelimit(key='user', rate='30/m', method=['GET','POST'],block=True),)
    def roles(self, request, pk=None): #TODO role not created fix the bug
        project = self.get_object()
        #TODO make the single role fatch
        if request.method == "GET":
            roles = project.roles.filter(is_open=True)
            return Response(GetJobRoleSerializer(roles, many=True).data)

        if request.method == "POST":
            if project.owner != request.user:
                return Response({"detail": "Only the owner can add roles to this post."}, status=status.HTTP_403_FORBIDDEN)

            serializer = CreateJobRoleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                role = serializer.save(project=project)
                Project.objects.filter(id=project.id).update(
                    application_count=('application_count')+1
                )
                _safe_notify(notify_new_role_added, role)
            return Response(GetJobRoleSerializer(role).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="close")
    @method_decorator(ratelimit(key='user', rate='5/m', method='POST',block=True),)
    def close_project(self, request, pk=None):
        project = self.get_object()
        if project.owner != request.user:
            return Response({"detail": "Only the owner can close this post."}, status=status.HTTP_403_FORBIDDEN)
        project.is_active = False
        project.save(update_fields=["is_active"])
        _safe_notify(notify_project_closed, project)
        return Response({"message": f"Post '{project.title}' closed successfully."})

    @action(detail=True, methods=["post",'GET'], url_path="Project_memeber")
    def get_project_member(self,request,pk=None):
        project=self.get_object()
        cache_member=cache.get(f'project_memeber{project.id}')
        if cache_member:
            return Response(cache_member,status.HTTP_200_OK)

        data=Membership.objects.filter(project=project).select_related('user').order_by('joined_at')
        ser= MemebrSerializer(data,many=True)
        cache.set(f'project_memeber{project.id}',ser.data,timeout=400)
        return Response({
            "data":ser.data
        },status.HTTP_200_OK)
        
    #TODO make role edit endpoint
        
        

'''
this all class for only project owner manage and see all appliction
status and perform all task

'''
#! accpect appliction 
class AccpectAppliction(APIView):
    permission_classes = [IsAuthenticated,IsProjectOwner]

    def post(self, request, appliction_id):
        appliction = get_object_or_404(Application, id=appliction_id)
        if appliction.role.project.owner != request.user:
            return Response({"detail": "Only post owner can accept applications."}, status=status.HTTP_403_FORBIDDEN)

        if appliction.status == Application.Status.ACCEPTED:
            return Response({"message": "Already accepted this application"}, status=status.HTTP_400_BAD_REQUEST)

        appliction.status = Application.Status.ACCEPTED
        Membership.objects.get_or_create(
            user=appliction.user,
            project=appliction.role.project,
            defaults={"role_title": appliction.apply_role_purpose or appliction.role.title, "is_active": True}
        )
        cache.delete(f'project_memeber{appliction.role.project.id}')
        cache.delete(f'single_appliction{appliction_id}')
        
        appliction.save(update_fields=["status"])
        _safe_notify(notify_application_accepted, appliction)
        _safe_notify(notify_new_member, appliction.role.project, appliction.user)
        return Response({"message": f"{appliction.user.username} application accepted for post {appliction.role.project.title}"})

#! rejected appliction
class RejectAppliction(APIView):
    permission_classes = [IsAuthenticated,IsProjectOwner]

    def post(self, request, appliction_id):
        appliction = get_object_or_404(Application, id=appliction_id)
        if appliction.role.project.owner != request.user:
            return Response({"detail": "Only post owner can reject applications."}, status=status.HTTP_403_FORBIDDEN)

        if appliction.status == Application.Status.REJECTED:
            return Response({"message": "Already rejected this application"}, status=status.HTTP_400_BAD_REQUEST)

        appliction.status = Application.Status.REJECTED
        appliction.save(update_fields=["status"])
        cache.delete(f'single_appliction{appliction_id}')
        _safe_notify(notify_application_rejected, appliction)
        return Response({"message": f"{appliction.user.username} application rejected for post {appliction.role.project.title}"})


#! this class give apply appliction list
class RoleApplictionPendingListView(APIView):
    
    def get(self,request,role_id):
        role=get_object_or_404(RoleNeeded,id=role_id)
        print(role.title)
        if role.project.owner!= request.user:
            return Response({
                "message":"only owner see pending list"
            },status.HTTP_400_BAD_REQUEST)
        appliction=Application.custom_objects.get_pending_appliction().filter(role=role).select_related('user').order_by('created_at')
        ser=GetapplictionSerializar(appliction,many=True)
        return Response(ser.data)
        
class RoleApplictionAccpectedListView(APIView):
    
    def get(self,request,role_id):
        role=get_object_or_404(RoleNeeded,id=role_id)
        print(role.title)
        if role.project.owner!= request.user:
            return Response({
                "message":"only owner see pending list"
            },status.HTTP_400_BAD_REQUEST)
        appliction=Application.custom_objects.get_accpected_appliction().filter(role=role).select_related('user').order_by('created_at')
        ser=GetapplictionSerializar(appliction,many=True)
        return Response(ser.data)
        
class RoleApplictionRejectedListView(APIView):
    permission_classes=[IsProjectOwner,IsAuthenticated]
    
    def get(self,request,role_id):
        role=get_object_or_404(RoleNeeded,id=role_id)
        print(role.title)
        if role.project.owner!= request.user:
            return Response({
                "message":"only owner see pending list"
            },status.HTTP_400_BAD_REQUEST)
        appliction=Application.custom_objects.get_rejected_appliction().filter(role=role).select_related('user').order_by('created_at')
        ser=GetapplictionSerializar(appliction,many=True)
        return Response(ser.data)
        

class SingleApplictionDetils(APIView):
    
    permission_classes=[IsProjectOwner,IsAuthenticated]
    
    def get(self,request,appliction_id):
        cache_appliction= cache.get(f'single_appliction{appliction_id}')
        if cache_appliction:
            return Response(cache_appliction)
        appliction=Application.objects.get(id=appliction_id)
        if not appliction:
            return Response('appliction not found',status.HTTP_400_BAD_REQUEST)
        ser=GetapplictionSerializar(appliction)
        cache.set(f'single_appliction{appliction_id}',ser.data,timeout=300)
        return Response(ser.data,status.HTTP_200_OK)
        
        


''''
this class for applide user see and manage all task and peform 
all task 

'''
class LeaveProjectView(APIView):
    permission_classes = [IsAuthenticated,IsProjectMember]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        membership = get_object_or_404(Membership, project=project, user=request.user, is_active=True)
        membership.is_active = False
        membership.save(update_fields=["is_active"])
        cache.delete(f'project_memeber{project_id}')
        _safe_notify(notify_member_left, project, request.user)
        return Response({"message": f"You have left post project {project.title}."})


class WithdrawAppliction(APIView):
    permission_classes = [IsAuthenticated,Isowner]

    def post(self, request, appliction_id):
        appliction = get_object_or_404(Application, id=appliction_id, user=request.user)
        with transaction.atomic():
            Project.objects.filter(id=appliction.role.project.id).update(
            application_count=('application_count')-1)          
            _safe_notify(notify_application_withdrawn, appliction)
            appliction.delete()
        return Response({"message": "Application withdrawn successfully."})

#! cretae appliction endpint
class ApplictionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, roleNeed_id):
        role = get_object_or_404(RoleNeeded, id=roleNeed_id)
        if not role.is_open or role.slots_available <= 0:
            return Response({"detail": "This role is closed for applications."}, status=status.HTTP_400_BAD_REQUEST)

        existing_app = Application.objects.filter(user=request.user, role=role).first()
        if existing_app:
            return Response({"detail": "You have already applied for this role."}, status=status.HTTP_400_BAD_REQUEST)

        ser = ApplictionSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        appliction = ser.save(role=role)
        _safe_notify(notify_application_received, appliction)
        return Response({"message": f"Applied successfully for {role.title} in {role.project.title}"}, status=status.HTTP_201_CREATED)
    
#! this class give single and list of appliction for applide user
class AppliedUserApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, application_id=None):
        if application_id:
            application = get_object_or_404(Application, id=application_id, user=request.user)
            serializer = AppliedApplictionSerializer(application)
            return Response(serializer.data)

        queryset = Application.objects.filter(user=request.user)
        serializer = AppliedApplictionSerializer(queryset, many=True)
        return Response(serializer.data)
class AppliedUserAccpetedApplictionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        data=Application.custom_objects.get_accpected_appliction().filter(user=request.user)
        serializer=AppliedApplictionSerializer(data,many=True)
        return Response(serializer.data)

#TODO list of join projects

