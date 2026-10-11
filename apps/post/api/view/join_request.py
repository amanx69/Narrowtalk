from ..serializers import SentRequestSerializer, GetRequestJoinProjectDetailSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ...models import RequestJoinProjet ,Membership
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from core.permissions import IsJoinRequestReceiver 
from django.db.models import F
from apps.Chats.service import join_in_project_groupe
from ..service import Update_profile_project_join
from services.email_services import JoinRequestSentMail, JoinRequestAcceptedMail
from apps.notification.api.service import notify_join_request_sent, notify_join_request_accepted
from ..service import _safe_notify
from core.throttling import (
    SendJoinRequestThrottle,
    acceptJoinRequestThrottle,
    rejectJoinRequestThrottle,
    
)




from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

class SendRequestForJoinProject(generics.CreateAPIView):
    
    serializer_class= SentRequestSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[SendJoinRequestThrottle]
    def perform_create(self, serializer):
        try:
            join_req = serializer.save(request_owner=self.request.user)
            JoinRequestSentMail.delay(join_req.id)
            _safe_notify(notify_join_request_sent,join_req)
        except IntegrityError:
            raise ValidationError({"detail": "You have already sent a request to this user for this role."})
    
        
        
# accepted request views

class AcceptJoinRequest(APIView):
    permission_classes=[IsAuthenticated, IsJoinRequestReceiver]
    throttle_classes=[acceptJoinRequestThrottle]
    def patch(self,request,request_id):
        queryset = RequestJoinProjet.objects.select_related('project', 'role', 'receiver_user')
        obj = get_object_or_404(queryset, id=request_id)
        self.check_object_permissions(request, obj)
        
        if obj.status == RequestJoinProjet.Status.ACCEPTED:
            return Response({
                "message":" you already accepted this request"
            },status.HTTP_400_BAD_REQUEST)
        if obj.status != RequestJoinProjet.Status.PENDING:
            return Response(
                {"detail": "Request is already processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        #  Agar user already active member hai toh reject kar do
        if Membership.objects.filter(user=request.user, project=obj.project, is_active=True).exists():
            return Response(
                {"detail": "You are already an active member of this project."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            obj.status = RequestJoinProjet.Status.ACCEPTED
            Membership.objects.update_or_create(
                user=request.user,
                project=obj.project,
                defaults={
                    'role_title': obj.role.role,
                    'is_active': True
                }
            )   
            join_in_project_groupe(obj.project, request.user, request)
                
            if obj.role.slots_available > 0:
                obj.role.slots_available = F('slots_available') - 1
                obj.role.save(update_fields=['slots_available'])
                
            obj.project.member_count = F('member_count') + 1
            obj.project.save(update_fields=['member_count'])
                # update the jion profile field for new join user
            Update_profile_project_join.delay(request.user.user_profile.id)
            obj.save(update_fields=['status'])
            
            JoinRequestAcceptedMail.delay(obj.id)
            _safe_notify(notify_join_request_accepted, obj)
        return Response({"message":"join project succussfully"},status.HTTP_200_OK)


class RejectJoinRequest(APIView):
    permission_classes = [IsAuthenticated, IsJoinRequestReceiver]
    throttle_classes=[rejectJoinRequestThrottle]
    
    def patch(self, request, request_id):
        queryset = RequestJoinProjet.objects.select_related('receiver_user')
        obj = get_object_or_404(queryset, id=request_id)
        self.check_object_permissions(request, obj)  
        if obj.status != RequestJoinProjet.Status.PENDING:
            return Response(
                {"detail": "Request is already processed."},
                status=status.HTTP_400_BAD_REQUEST
            )  
        obj.status = RequestJoinProjet.Status.REJECTED
        obj.save(update_fields=['status'])
        return Response({"message": "Join request rejected successfully"}, status=status.HTTP_200_OK)
     

from ...models import Project
from ..serializers import ProjectNameSerializer
# this api create for fatch current-user project with name for select the project to send the request
class CurrentUserProjectNamesAPIView(generics.ListAPIView):
    serializer_class = ProjectNameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).only('id', 'project_name')




from ..serializers import GetRequestJoinProjectListSerializer
class CurrentUserPendingRequestsListAPIView(generics.ListAPIView):
    serializer_class = GetRequestJoinProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestJoinProjet.objects.filter(
            receiver_user=self.request.user, 
            status=RequestJoinProjet.Status.PENDING
        ).select_related('project', 'role', 'request_owner__user_profile')

class CurrentUserPendingRequestDetailAPIView(generics.RetrieveAPIView):
    serializer_class = GetRequestJoinProjectDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RequestJoinProjet.objects.filter(
            receiver_user=self.request.user,
            status=RequestJoinProjet.Status.PENDING
        ).select_related('project', 'role', 'request_owner__user_profile')

from ..serializers import SentRequestJoinProjectListSerializer

class CurrentUserSentRequestsListAPIView(generics.ListAPIView):
    serializer_class = SentRequestJoinProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestJoinProjet.objects.filter(
            request_owner=self.request.user
        ).select_related('project', 'role', 'receiver_user__user_profile')

from ..serializers import SentRequestJoinProjectDetailSerializer

class CurrentUserSentRequestDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SentRequestJoinProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestJoinProjet.objects.filter(
            request_owner=self.request.user
        ).select_related('project', 'role', 'receiver_user__user_profile')