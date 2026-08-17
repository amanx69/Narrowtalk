from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import Profileserlizsers
from rest_framework.permissions import IsAuthenticated
from ..permssion import Isowner
from .serializer import Profileserlizsers
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.decorators import api_view ,permission_classes
User=get_user_model()


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
def ShareProfile(request,Profile_id):
    pass


 
    
     
    
    