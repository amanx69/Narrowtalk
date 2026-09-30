from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from ..models import UserBlock
from rest_framework.generics import CreateAPIView
from .serializers import ReportSerializer
from apps.post.models import Membership
User = get_user_model()



class BlockUser(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self,request,user_id):
        if request.user.id == user_id:
            return Response({"error": "You cannot block yourself."},
            status=status.HTTP_400_BAD_REQUEST)
            
        target_user=get_object_or_404(User,id=user_id)
        my_project_ids = Membership.objects.filter(user=request.user, is_active=True).values_list('project_id', flat=True)
        shared_membership = Membership.objects.filter(user=target_user, project_id__in=my_project_ids, is_active=True).exists()
        
        # 2. Check if I am the owner and target is member, OR target is owner and I am member
        is_my_member = Membership.objects.filter(project__owner=request.user, user=target_user, is_active=True).exists()
        am_i_their_member = Membership.objects.filter(project__owner=target_user, user=request.user, is_active=True).exists()
        
        if shared_membership or is_my_member or am_i_their_member:
            return Response({
                "error": "You cannot block someone you share an active project with. Please remove them or leave the project first."
            }, status=status.HTTP_403_FORBIDDEN)
        block, created = UserBlock.objects.get_or_create(
            blocker=request.user, 
            blocked_user=target_user
        )
        if created:
            return Response({"message": f"You have blocked {target_user.username}"}, status=status.HTTP_201_CREATED)
        else:
            block.delete()
            return Response({
                "message": f"You have unblocked {target_user.username}"
            },status.HTTP_200_OK)
        
        
        
        
    
class ReportCreateView(CreateAPIView):
    serializer_class=ReportSerializer
    permission_classes=[permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)