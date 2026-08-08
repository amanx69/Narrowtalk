from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import Profileserlizsers
from rest_framework.permissions import IsAuthenticated
from ..permssion import Isowner
from rest_framework.parsers import MultiPartParser ,FormParser

class ProfileView(RetrieveUpdateAPIView):
    serializer_class=Profileserlizsers
    permission_classes=[IsAuthenticated,Isowner]
  

    def get_object(self):
        return self.request.user.user_profile
    
    
    
    
    