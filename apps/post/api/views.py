from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action 
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from ..models import Project, Membership, RoleNeeded, Application
from .serializers import ProjectSerializer, GetJobRoleSerializer, CreateJobRoleSerializer, ApplictionSerializer
from core.permissions import IsOwnerOrReadOnly,Isowner,IsProjectOwner ,IsProjectMember
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
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectSerializer


    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        notify_post_created(project)

    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH'))
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        project = ser.save()
        notify_post_updated(project)
        return Response(ser.data)

    def perform_destroy(self, instance, *args, **kwargs):
        notify_project_closed(instance)
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @action(detail=True, methods=["get", "post"], url_path="create_job_role")
    def roles(self, request, pk=None):
        project = self.get_object()

        if request.method == "GET":
            roles = project.roles.filter(is_open=True)
            return Response(GetJobRoleSerializer(roles, many=True).data)

        if request.method == "POST":
            if project.owner != request.user:
                return Response({"detail": "Only the owner can add roles to this post."}, status=status.HTTP_403_FORBIDDEN)

            serializer = CreateJobRoleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            role = serializer.save(project=project)
            notify_new_role_added(role)
            return Response(GetJobRoleSerializer(role).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="close")
    def close_project(self, request, pk=None):
        project = self.get_object()
        if project.owner != request.user:
            return Response({"detail": "Only the owner can close this post."}, status=status.HTTP_403_FORBIDDEN)
        project.is_active = False
        project.save(update_fields=["is_active"])
        notify_project_closed(project)
        return Response({"message": f"Post '{project.title}' closed successfully."})


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
        notify_application_received(appliction)
        return Response({"message": f"Applied successfully for {role.title} in {role.project.title}"}, status=status.HTTP_201_CREATED)


class WithdrawAppliction(APIView):
    permission_classes = [IsAuthenticated,Isowner]

    def post(self, request, appliction_id):
        appliction = get_object_or_404(Application, id=appliction_id, user=request.user)
        notify_application_withdrawn(appliction)
        appliction.delete()
        return Response({"message": "Application withdrawn successfully."})


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
        appliction.save(update_fields=["status"])
        notify_application_accepted(appliction)
        notify_new_member(appliction.role.project, appliction.user)
        return Response({"message": f"{appliction.user.username} application accepted for post {appliction.role.project.title}"})


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
        notify_application_rejected(appliction)
        return Response({"message": f"{appliction.user.username} application rejected for post {appliction.role.project.title}"})



class LeaveProjectView(APIView):
    permission_classes = [IsAuthenticated,IsProjectMember]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        membership = get_object_or_404(Membership, project=project, user=request.user, is_active=True)
        membership.is_active = False
        membership.save(update_fields=["is_active"])
        notify_member_left(project, request.user)
        return Response({"message": f"You have left post project {project.title}."})

    


