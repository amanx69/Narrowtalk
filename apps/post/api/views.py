from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action 
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
import datetime
from django.utils import timezone 
from rest_framework import generics
from django.db import transaction
from django.utils.decorators import method_decorator
from django.db.models import F
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
from core.throttling import *
from django.core.cache import cache
from ..models import Project, Membership, RoleNeeded, Application
from .serializers import (
    ProjectSerializer, 
    GetJobRoleSerializer, 
    CreateJobRoleSerializer,
    ApplictionSerializer,
    MemebrSerializer,
    GetapplictionSerializar,
    AppliedApplictionListSerializer,
    ProjectJoinSerializer,
    AppliedApplictionDetilesSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
     GetapplictionDetileSerializar,
    
    
    )
from core.permissions import IsOwnerOrReadOnly,Isowner,IsProjectOwner ,IsProjectMember,IsRoleOwner ,IsProjectownerRemove
from .service import _safe_notify ,Update_profile_project_join ,decrement_profile_project_join
from apps.notification.api.service import (
  
    notify_application_received,
    notify_application_accepted,
    notify_application_rejected,
    notify_application_withdrawn,

)
from services.email_services import AccpectedAppliction_email ,RemoveProjectMail


class ProjectView(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = ProjectSerializer
    filter_backends=[filters.SearchFilter]
    search_fields=['^project_name','is_active']
    #! setup throttles
    def get_throttles(self):
        if self.action =='create':
            return [ProjectCreatethrottle()]
        elif self.action in ['update', 'partial_update']:
            return [ProjectUpdatethrottle()]
        elif self.action =='destroy':
            return [ProjectDeletethrottle()]
        elif self.action == "roles":
            if self.request.method=='POST':
                return [RoleCreatethrottle()]
        elif self.action =='role_detail':
            if self.request.method=='PATCH':
                return [RoleUpdatethrottle()]
        elif self.action== "delete_role":
            if self.request.method=="DELETE":
                return [RoleDeletethrottle()]
                
        return super().get_throttles()
#! i override the ser only for retrieve project list of current user
    def get_serializer_class(self): 
        if self.action =="retrieve":
            return  ProjectDetailSerializer
        if self.action =="list":
            return ProjectListSerializer
        
        return self.serializer_class
    
    def get_queryset(self):  
        if self.action =="list":  
            return Project.objects.filter(is_active=True,is_delete=False,owner=self.request.user)
        return Project.objects.all()

    def perform_create(self, serializer):
            project = serializer.save(owner=self.request.user)
          

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        project = ser.save()
        return Response(ser.data)

    def perform_destroy(self, instance, *args, **kwargs):
        instance.is_active = False
        instance.is_delete=True
        instance.save(update_fields=["is_active",'is_delete'])
  #! create a role and get all project role 
    @action(detail=True, methods=["get", "post"], url_path="create_job_role")
    def roles(self, request, pk=None): 
        project = self.get_object()
       
        if request.method == "GET":
            roles = project.roles.filter(is_open=True)
            return Response(GetJobRoleSerializer(roles, many=True).data)
        if request.method == "POST":
            if project.owner != request.user:
                raise PermissionDenied("Only the owner can add roles to this post.")

            serializer = CreateJobRoleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                role = serializer.save(project=project)
                role.project.role_count = F("role_count") + 1
                role.project.save(update_fields=['role_count'])
                #TODO make count if new role create than inc in project role count
            return Response(GetJobRoleSerializer(role).data, status=status.HTTP_201_CREATED)
#! close the project
    @action(detail=True, methods=["post"], url_path="close")
    def close_project(self, request, pk=None):
        project = self.get_object()
        if project.owner != request.user:
            raise PermissionDenied('Only owner can change this setting')
        project.is_active = False
        project.save(update_fields=["is_active"])
        
        
        return Response({"message": f"Post '{project.title}' closed successfully."})
 #! give project meneber
    @action(detail=True, methods=['GET'], url_path="Project_memeber")
    def get_project_member(self,request,pk=None):
        project=self.get_object()
        cache_member=cache.get(f'project_memeber{project.id}')
        if cache_member:
            return Response(cache_member,status.HTTP_200_OK)

        data=Membership.objects.filter(project=project,is_active=True).select_related('user').order_by('joined_at')
        ser= MemebrSerializer(data,many=True)
        cache.set(f'project_memeber{project.id}',ser.data,timeout=400)
        return Response({
            "data":ser.data
        },status.HTTP_200_OK)
    #! get single and update the role
    @action(detail=True, methods=["get", "patch"], url_path=r"role/(?P<role_id>[^/.]+)",url_name="edit_and_get_role",permission_classes=[IsAuthenticated])
    def role_detail(self, request, pk=None, role_id=None):
        project = self.get_object()
        role = get_object_or_404(project.roles, id=role_id)

        if request.method == "GET":
            return Response(GetJobRoleSerializer(role).data)

        if project.owner != request.user:
            raise PermissionDenied('Only the owner can edit this role')

        serializer = CreateJobRoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(GetJobRoleSerializer(role).data)
    @action(detail=True, methods=["delete"], url_path=r"delete_role/(?P<role_id>[^/.]+)",url_name="delete_role")
    def delete_role(self, request, pk=None, role_id=None):
        project = self.get_object()
        role = get_object_or_404(project.roles, id=role_id)
        if project.owner != request.user:
            raise PermissionDenied('Only the owner can delete this role')
        with transaction.atomic():
            role.project.role_count = F("role_count") - 1
            role.project.save(update_fields=['role_count'])
            role.delete()
        return Response({"message": f"Role '{role.title}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        

'''
this all class for only project owner manage and see all appliction
status and perform all task

'''
#! accpect appliction 
class AccpectAppliction(APIView):
    permission_classes = [IsAuthenticated,IsProjectOwner]
    throttle_classes=[ApplictionAccpectthrottle]
    

    def post(self, request, appliction_id):
        
        appliction = get_object_or_404(Application, id=appliction_id,)
        self.check_object_permissions(request, appliction)
        if appliction.status == Application.Status.ACCEPTED:
            return Response({"message": "Already accepted this application"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            appliction.status = Application.Status.ACCEPTED
            
            Membership.objects.update_or_create(
                user=appliction.user,
                project=appliction.role.project,
                defaults={
                    'role_title': appliction.apply_role_purpose,
                    'is_active': True
                }
            )
            
            if appliction.role.slots_available > 0:
                appliction.role.slots_available = F('slots_available') - 1
                appliction.role.save(update_fields=['slots_available'])
           
            appliction.role.project.member_count=F('member_count')+1
            appliction.role.project.save(update_fields=['member_count'])
            appliction.save(update_fields=["status"])
            _safe_notify(notify_application_accepted, appliction)
            Update_profile_project_join.delay(appliction.user.user_profile.id)
            AccpectedAppliction_email.delay(appliction.id)
            cache.delete(f'project_memeber{appliction.role.project.id}')
            cache.delete(f'single_appliction{appliction_id}')
            
        return Response({"message": f"{appliction.user.username} application accepted for post {appliction.role.project.project_name}"},status.HTTP_200_OK)

#! rejected appliction
class RejectAppliction(APIView):
    permission_classes = [IsAuthenticated,IsProjectOwner]
    throttle_classes=[ApplictionRejectthrottle]

    def post(self, request, appliction_id):
        appliction = get_object_or_404(Application, id=appliction_id)
        self.check_object_permissions(request,appliction)
        if appliction.status == Application.Status.REJECTED:
            return Response({"message": "Already rejected this application"}, status=status.HTTP_400_BAD_REQUEST)

        appliction.status = Application.Status.REJECTED
        appliction.save(update_fields=["status"])            
        cache.delete(f'single_appliction{appliction_id}')
        _safe_notify(notify_application_rejected, appliction)
        return Response({"message": f"{appliction.user.username} application rejected for post {appliction.role.project.title}"},status.HTTP_200_OK)


#! this class give apply appliction list
class RoleApplictionPendingListView(APIView):
    permission_classes = [IsAuthenticated,IsProjectOwner]
    
    def get(self,request,role_id):
        role=get_object_or_404(RoleNeeded,id=role_id)
        if role.project.owner!= request.user:
            raise PermissionDenied('only owner see pending list')
        
        appliction=Application.custom_objects.get_pending_appliction().filter(role=role).select_related('user').order_by('created_at')
        ser=GetapplictionSerializar(appliction,many=True)
        return Response(ser.data,status.HTTP_200_OK)
        
class RoleApplictionAccpectedListView(APIView):
    permission_classes = [IsAuthenticated,IsProjectOwner]
    
    def get(self,request,role_id):
        role=get_object_or_404(RoleNeeded,id=role_id)
        if role.project.owner!= request.user:
            raise PermissionDenied('only owner see accpected list')
        
        appliction=Application.custom_objects.get_accpected_appliction().filter(role=role).select_related('user').order_by('created_at')
        ser=GetapplictionSerializar(appliction,many=True)
        return Response(ser.data)
        
class RoleApplictionRejectedListView(APIView):
    permission_classes=[IsProjectOwner,IsAuthenticated]
    
    def get(self,request,role_id):
        role=get_object_or_404(RoleNeeded,id=role_id)
        if role.project.owner!= request.user:
            raise PermissionDenied('only owner see rejected list')
        appliction=Application.custom_objects.get_rejected_appliction().filter(role=role).select_related('user').order_by('created_at')
        ser=GetapplictionSerializar(appliction,many=True)
        return Response(ser.data)
        

class SingleApplictionDetils(APIView):
    permission_classes=[IsAuthenticated,IsProjectOwner]
    
    def get(self,request,appliction_id):
        cache_appliction= cache.get(f'single_appliction{appliction_id}')
        if cache_appliction:
            return Response(cache_appliction)
        
        appliction=get_object_or_404(Application,id=appliction_id)
        self.check_object_permissions(request,appliction)
        ser= GetapplictionDetileSerializar(appliction)
        cache.set(f'single_appliction{appliction_id}',ser.data,timeout=300)
        return Response(ser.data,status.HTTP_200_OK)
        
        
        
        
#! this class used for remove the member in project    
class RemoveMemberView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsProjectownerRemove]
    throttle_classes=[RemoveMemberThrottle]
    
    def get_object(self):
        obj = get_object_or_404(
            Membership,
            user_id=self.kwargs['user_id'],
            project_id=self.kwargs['project_id']
        )
        self.check_object_permissions(self.request, obj)
        return obj
    
    def perform_destroy(self, instance):
        user = instance.user
        project = instance.project
        
        with transaction.atomic():
            if project.member_count > 0:
                project.member_count = F('member_count') - 1
                project.save(update_fields=['member_count'])
                
            if user.user_profile.project_joined > 0:
                user.user_profile.project_joined = F("project_joined") - 1
                user.user_profile.save(update_fields=['project_joined'])
                
            #TODO send email and not notifiction
            RemoveProjectMail.delay(user.id,project.project_name)
            instance.is_active=False
            instance.save(update_fields=['is_active'])
            
        
        


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
        
        if project.member_count > 0:
            project.member_count = F('member_count') - 1
            project.save(update_fields=['member_count'])
        decrement_profile_project_join.delay(membership.user.user_profile.id)
        membership.save(update_fields=["is_active"])
        cache.delete(f'project_memeber{project_id}')
        return Response({"message": f"You have left post project {project.title}."})


class WithdrawAppliction(APIView): # TODO think about this api if need than not delete otherwise delete
    permission_classes = [IsAuthenticated,Isowner]

    def delete(self, request, appliction_id):
        appliction = get_object_or_404(Application, id=appliction_id, user=request.user)
        with transaction.atomic():
            RoleNeeded.objects.filter(id=appliction.role.id).update(
            application_count=F('application_count')-1)          
            _safe_notify(notify_application_withdrawn, appliction)
            appliction.delete()
        return Response({"message": "Application withdrawn successfully."},status.HTTP_200_OK)

#! cretae appliction endpint
class ApplictionView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes=[ApplictionCreatethrottle]
    def post(self, request, roleNeed_id):
        role = get_object_or_404(RoleNeeded, id=roleNeed_id)
        if role.project.owner == request.user:
            raise PermissionDenied("you can't apply own project")
        if not role.is_open or role.slots_available <= 0:
            return Response({"detail": "This role is closed for applications."}, status=status.HTTP_400_BAD_REQUEST)

        existing_app = Application.objects.filter(user=request.user, role=role).order_by('-created_at').first()
        
        if existing_app:
            if existing_app.status == Application.Status.ACCEPTED:
                return Response({"detail":"you already accepted for this role"}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_app.status == Application.Status.PENDING:
                return Response({"detail":"please wait project owner response before re-appily"}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_app.status == Application.Status.REJECTED:
                #! 7-day cooldown period since their last application
                days_since_applied = (timezone.now() - existing_app.created_at).days
                if days_since_applied < 3:
                    days_left = 3 - days_since_applied
                    return Response(
                        {"detail": f"You were recently rejected. Please wait {days_left} more day(s) before re-applying to improve yourself"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        ser = ApplictionSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            if not existing_app:
                role.application_count = F('application_count') + 1
                role.save(update_fields=['application_count']) 
            appliction = ser.save(role=role)
            _safe_notify(notify_application_received, appliction)
            #TODO send mail to owner new applict
        return Response({"message": f"Applied successfully for {role.title} in {role.project.project_name}"}, status=status.HTTP_201_CREATED)
    
#! this class give single and list of appliction for applide user
class AppliedUserApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, application_id=None):
        if application_id:
            application = get_object_or_404(Application, id=application_id, user=request.user)
            serializer = AppliedApplictionDetilesSerializer(application) 
            return Response(serializer.data)

        queryset = Application.objects.filter(user=request.user)
        serializer = AppliedApplictionListSerializer(queryset, many=True)
        return Response(serializer.data,status.HTTP_200_OK)
    #! this class give list of accpected appliction
class AppliedUserAccpetedApplictionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        data=Application.custom_objects.get_accpected_appliction().filter(user=request.user)
        serializer=AppliedApplictionListSerializer(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)
#! this class return all project where user join 
class UserJoinProjectDetiles(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
    
        project=Membership.objects.filter(user=request.user).select_related('project')
        ser=ProjectJoinSerializer(project,many=True)
        return Response(ser.data,status.HTTP_200_OK)
        
    

#! make project owner also send request to join
#! user show and accpected