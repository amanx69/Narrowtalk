from rest_framework.generics import RetrieveUpdateAPIView,RetrieveAPIView
from .serializer import Profileserlizsers
from rest_framework.permissions import IsAuthenticated
from ..permssion import Isowner
from .serializer import Profileserlizsers
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.decorators import api_view ,permission_classes
User=get_user_model()
from ..models import *
from django.shortcuts import get_object_or_404
from .service import Profile_like
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

#! this class handle update and get profile 
from django.core.cache import cache
from rest_framework.response import Response

class ProfileView(RetrieveUpdateAPIView):
    serializer_class = Profileserlizsers
    permission_classes = [IsAuthenticated, Isowner]

    def get_object(self):
        return self.request.user.user_profile

    def retrieve(self, request, *args, **kwargs):
        cache_key = f"user_profile:{request.user.id}"
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
        
        
#TODO make share profile endpoint

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ShareProfile(request,user_id):
    
    url=f'http://127.0.0.1:8000/api/v1/Profile/other_profile/{user_id}/'
    return Response(url,200)


 
    
#! like and unlike view     
class ProflieLikeView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,Profile_id):
        profile= get_object_or_404(Profile,id=Profile_id)
        response= Profile_like(request.user,profile)
        return response
        
        
    
#! other user profile
class GetOtherUserProfile(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=Profileserlizsers
    
    def get_object(self):
        user=get_object_or_404(User,id=self.kwargs['user_id'])
        return user.user_profile
   
    
    
    
      