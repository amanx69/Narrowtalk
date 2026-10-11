from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F
from django.core.cache import cache
from apps.Profile.models import Profile
from apps.Chats.models import ChatGroup, GroupMember
from ...models import Membership, Project, RoleNeeded
from core.permissions import IsProjectOwnerForProject
from ..service import Decrement_Project_Create_Count, Increment_Project_Create_Count
from core.throttling import TransferOwnershipThrottle,CompleteProjectThrottle

class UpdateProjectIscompleated(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwnerForProject]
    throttle_classes=[CompleteProjectThrottle]

    def post(self, request, project_id=None, pk=None):
        target_id = project_id or pk
        project = get_object_or_404(Project, id=target_id, is_delete=False)
        self.check_object_permissions(request, project)

        if project.status == Project.ProjectStatus.COMPLETED:
            return Response(
                {"error": "This project is already marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            project.status = Project.ProjectStatus.COMPLETED
            project.save(update_fields=['status', 'updated_at'])
            RoleNeeded.objects.filter(project=project).update(
                is_open=False,
                is_complete=True
            )

            member_user_ids = list(
                Membership.objects.filter(
                    project=project,
                    is_active=True
                ).values_list('user_id', flat=True)
            )
            all_user_ids = set(member_user_ids)
            all_user_ids.add(project.owner_id)
            updated_profiles_count = Profile.objects.filter(
                user_id__in=all_user_ids
            ).update(
                project_completed=F('project_completed') + 1
            )
            # Invalidate caches for updated member profiles and project
            for uid in all_user_ids:
                cache.delete(f"user_profile_v1_:{uid}")
                cache.delete(f"other_profile_v2_:{uid}")
            cache.delete(f"project_detail_v1_:{project.id}")
            #TODO send notifiction all member
        return Response(
            {
                "message": "Project has been marked as completed successfully.",
                "project_id": str(project.id),
                "status": project.status,
                "completed_members_count": len(all_user_ids),
                "profiles_updated": updated_profiles_count
            },
            status=status.HTTP_200_OK
        )


class TransferProjectOwnershipView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwnerForProject]
    throttle_classes=[TransferOwnershipThrottle]

    def post(self, request, project_id=None, pk=None):
        target_id = project_id or pk
        project = get_object_or_404(Project, id=target_id, is_delete=False)
        self.check_object_permissions(request, project)
        new_owner_id = request.data.get('new_owner_id')
        if not new_owner_id:
            return Response(
                {"error": "new_owner_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if str(new_owner_id) == str(request.user.id):
            return Response(
                {"error": "You are already the owner of this project."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validate UUID format
        try:
            import uuid
            uuid.UUID(str(new_owner_id))
        except (ValueError, AttributeError):
            return Response(
                {"error": "Invalid new_owner_id format. Must be a valid UUID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Target user project ka active member hona chahiye
        new_owner_membership = Membership.objects.filter(
            project=project,
            user_id=new_owner_id,
            is_active=True
        ).select_related('user').first()

        if not new_owner_membership:
            return Response(
                {"error": "The specified user is not an active member of this project."},
                status=status.HTTP_400_BAD_REQUEST
            )


        old_owner = request.user
        new_owner = new_owner_membership.user

        with transaction.atomic():
            # Project owner change karein
            project.owner = new_owner
            project.save(update_fields=['owner', 'updated_at'])
            new_owner_membership.delete()
            old_owner_membership, created = Membership.objects.get_or_create(
                user=old_owner,
                project=project,
                defaults={'role_title': 'Previous Owner', 'is_active': True}
            )
            if not created:
                old_owner_membership.role_title = 'Previous Owner'
                old_owner_membership.is_active = True
                old_owner_membership.save(update_fields=['role_title', 'is_active'])
            try:
                chat_group = ChatGroup.objects.get(project=project)
                GroupMember.objects.filter(chat_group=chat_group, user=old_owner).update(
                    role=GroupMember.ChatRole.ADMIN
                )
                GroupMember.objects.filter(chat_group=chat_group, user=new_owner).update(
                    role=GroupMember.ChatRole.OWNER
                )
            except ChatGroup.DoesNotExist:
                pass

            #  update profile  project count
            if hasattr(old_owner, 'user_profile'):
                Decrement_Project_Create_Count(old_owner.user_profile.id)
            if hasattr(new_owner, 'user_profile'):
                Increment_Project_Create_Count(new_owner.user_profile.id)

            # delted caches
            cache.delete(f"user_profile_v1_:{old_owner.id}")
            cache.delete(f"user_profile_v1_:{new_owner.id}")
            cache.delete(f"other_profile_v2_:{old_owner.id}")
            cache.delete(f"other_profile_v2_:{new_owner.id}")
            cache.delete(f"project_detail_v1_:{project.id}")
            cache.delete(f"project_memeber_v1:{project.id}")


        return Response(
            {
                "message": "Project ownership transferred successfully.",
                "project_id": str(project.id),
                "new_owner": {
                    "id": str(new_owner.id),
                    "username": new_owner.username
                }
            },
            status=status.HTTP_200_OK
        )