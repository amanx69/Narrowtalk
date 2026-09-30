from rest_framework.generics import RetrieveUpdateAPIView,RetrieveAPIView 
from .serializer import Profileserlizsers
from rest_framework.permissions import IsAuthenticated
from ..permssion import Isowner
from .serializer import Profileserlizsers ,OtherUserProfileSerializer ,SearchResultProfileSerializer
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.decorators import api_view ,permission_classes
User=get_user_model()
from ..models import *
from django.shortcuts import get_object_or_404
from .service import Profile_like
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from decouple import config
#! this class handle update and get profile 
from rest_framework.response import Response
from core.throttling import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import NotFound
class ProfileView(RetrieveUpdateAPIView):
    serializer_class = Profileserlizsers
    permission_classes = [IsAuthenticated, Isowner]
    
    def get_throttles(self):
        if self.request.method  in ['PUT', 'PATCH']:
            return [ProfileUpdateThrottle()]
        return super().get_throttles()
    

    def get_object(self):
        return self.request.user.user_profile

    def retrieve(self, request, *args, **kwargs):
        cache_key = f"user_profile_v2_:{request.user.id}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)
    def perform_update(self, serializer):
        profile = serializer.save()
        cache.delete(f"user_profile:{profile.user.id}")
        
        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ShareProfile(request,user_id):
    url=f'{config('backend_url')}api/v1/Profile/other_profile/{user_id}/' #TODO change in prods
    return Response(url,200)


 
    
#! like and unlike view     
class ProflieLikeView(APIView):
    permission_classes=[IsAuthenticated]
    throttle_classes=[ProfileLikeThrottle]
    def post(self,request,Profile_id):
        profile= get_object_or_404(Profile,id=Profile_id)
        response= Profile_like(request.user,profile)
        return response
        
        
    
#! other user profile
class GetOtherUserProfile(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=OtherUserProfileSerializer
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        from apps.safety.models import UserBlock
        is_blocked = UserBlock.objects.filter(
            blocker=self.request.user, blocked_user_id=user_id
        ).exists() or UserBlock.objects.filter(
            blocker_id=user_id, blocked_user=self.request.user
        ).exists()
        
        if is_blocked:
            # Fake 404 error if blocked
            raise NotFound("This profile is unavailable or has been deleted.")
        profile = get_object_or_404(
            Profile.objects.prefetch_related('user__projects_owner'),
            user__id=user_id
        )
        return profile
   
    
    
    
      
      
#! search user endpoint


class SearchProfilesView(ListAPIView):
    serializer_class=SearchResultProfileSerializer
    permission_classes=[IsAuthenticated]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['^username','=user__email']
    def get_queryset(self):
        from apps.safety.models import UserBlock
        blocked_by_me = UserBlock.objects.filter(blocker=self.request.user).values_list('blocked_user_id', flat=True)
        blocked_me = UserBlock.objects.filter(blocked_user=self.request.user).values_list('blocker_id', flat=True)
        blocked_users_ids = set(blocked_by_me).union(set(blocked_me))
        
        return Profile.objects.exclude(user=self.request.user).exclude(user_id__in=blocked_users_ids)
    
    
    