from rest_framework import generics ,permissions
from rest_framework import status
from .serlizers import(
  SignUpSerializer ,
  LoginSerlizer,
  ForgetPasswordSerializer,
  ResetPasswordSerializer,
  VerifyEmailSerializer,
  resendverifySerializer
  )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from ..models import Emailverifiction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken
import hashlib
User=get_user_model()
#! signup

class SignUp(generics.CreateAPIView):

    permission_classes=[permissions.AllowAny]
    serializer_class= SignUpSerializer
    @method_decorator(ratelimit(key='ip', rate='6/h',method='POST'))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token=RefreshToken.for_user(user)
        return Response(
            {"message": "User registered successfully verify to continue",
             "access":str(token.access_token),
             "refresh":str(token)
             
             },
            status=status.HTTP_201_CREATED
        )
#! Login

class LoginView(APIView):
    
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='6/h',method='POST'))
    def post(self,request):
        serlizer= LoginSerlizer(data=request.data)
        serlizer.is_valid(raise_exception=True)
        user= serlizer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
                "message": "Login successful",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }
            }, status=status.HTTP_200_OK)
            
      



#! verify
class VerifyEmail(APIView):
    permission_classes=[]
    @method_decorator(ratelimit(key='ip', rate='5/h',method='GET'))
    def post(self,request):
        ser= VerifyEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        otp=ser.validated_data['otp']
        email=ser.validated_data['email']
        with transaction.atomic():
          
            Emailotp = Emailverifiction.objects.select_for_update().filter(
                user__email=email,
            ).first()
          
            if not Emailotp:
                return Response({"message":"otp is expire please resend again"},status.HTTP_400_BAD_REQUEST)
            if Emailotp.is_expire():
                return Response({
                    "message":"otp is expire please resend again"
                },status.HTTP_400_BAD_REQUEST)
            if Emailotp.attempts >=3:
                return Response({
                    "message":"to many attempts please resend again"
                },status.HTTP_400_BAD_REQUEST)
            if otp!=Emailotp.otp:
                Emailotp.attempts+=1
                Emailotp.save(update_fields=['attempts'])
                return Response({
                    "message":"Please enter a correct otp"
                },status.HTTP_400_BAD_REQUEST)
           
            Emailotp.user.is_verify = True
            Emailotp.used_it = True
            Emailotp.user.save(update_fields=["is_verify"])
            Emailotp.save(update_fields=["used_it"])
            Emailotp.delete()
            return Response({"message":"you email is verify continue yor journary"},status.HTTP_200_OK)
         

      
    

#! resend verify email
class ResendVerifyEmailView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/h',method='POST'))
    def post(self,request):
        ser=resendverifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email=ser.validated_data['email']
        user= User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({
                "message":"if your email i correct than check you email"
            },status=status.HTTP_200_OK)
        
        if user.is_verify:
            return Response({
                "message":"your email is already verified"
            },status=status.HTTP_200_OK)
        
        from .task import send_verification_email
        send_verification_email.delay(id=str(user.id))
        
        return Response({
            "message":"otp send on you email"
        },status=status.HTTP_200_OK)
            

    
        
        
#! forget password endpoint
from .task import send_reset_password_email
class SendForgetPassworEmaildView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='8/h',method='POST'))
    def post(self,request):
        ser=ForgetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user= User.objects.filter(email__iexact=ser.validated_data['email']).first()
        send_reset_password_email.delay(id=str(user.id))
        return Response({
            "message":"reset password link send you email check you email"
        },status=status.HTTP_200_OK)
        
#! reset password endpoint
class ResetPasswordView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='7/h',method='POST'))
    def post(self,request):
        
        ser=ResetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        password=ser.validated_data['password']
        email=ser.validated_data['email']
        otp=ser.validated_data['otp']
        with transaction.atomic():    

            Emailotp= Emailverifiction.objects.select_for_update().filter(
                user__email=email
            ).first()
            if not Emailotp:
                return Response({"message":"otp is expire please resend again"},status.HTTP_400_BAD_REQUEST)
                
            if Emailotp.is_expire():
                return Response({
                "message":"otp is expire please resend again"
                },status.HTTP_400_BAD_REQUEST)
            if Emailotp.attempts >=3:
                return Response({
                    "message":"to many attempts please resend again"
                },status.HTTP_400_BAD_REQUEST)
            if otp!=Emailotp.otp:
                Emailotp.attempts+=1
                Emailotp.save(update_fields=['attempts'])
                return Response({
                    "message":"Please enter a correct otp"
                    },status.HTTP_400_BAD_REQUEST)
                
          
                
            Emailotp.user.set_password(password)
            Emailotp.user.save(update_fields=["password"])
            Emailotp.used_it = True
            Emailotp.save(update_fields=["used_it"])
            Emailotp.delete()
        
        return Response({
            "message":"password reset successfully"
        },status=status.HTTP_200_OK)
        
        
#! logout endpoint

class LogoutView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST)