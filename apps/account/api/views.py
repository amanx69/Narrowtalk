from rest_framework import generics ,permissions
from rest_framework import status
from .serlizers import SignUpSerializer , LoginSerlizer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from ..models import Emailverifiction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User=get_user_model()
#! signup

class SignUp(generics.CreateAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class= SignUpSerializer
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {"message": "User registered successfully.", "user": user.id,
             "access": str(refresh.access_token),
            "refresh": str(refresh),
             
             },
            status=status.HTTP_201_CREATED
        )
#! Login

class LoginView(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        
        serlizer= LoginSerlizer(data=request.data)
        if serlizer.is_valid(raise_exception=True):
            user= serlizer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Login successful",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }
            }, status=status.HTTP_200_OK)
            
        return Response({
            "message":"somthing went wrong"
            },status=status.HTTP_400_BAD_REQUEST)
        
        



#! verify
class VerifyEmail(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request,token):
        EmailToken= get_object_or_404(Emailverifiction,token_hash=token)
        if EmailToken.is_expire() and EmailToken.used_it:
            return Response({
                "message":"your token is expire resent again",
            },status=status.HTTP_400_BAD_REQUEST)
        print(EmailToken.user.is_verify)  
        EmailToken.user.is_verify=True
        print(EmailToken.user.is_verify)
        EmailToken.used_it=True
        EmailToken.user.save()
        EmailToken.token_hash=""
        EmailToken.save()
        return Response({
            "message":"email verify compleated"
        },status=status.HTTP_200_OK )
        
        
        
        
