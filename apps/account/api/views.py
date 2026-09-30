from rest_framework import generics ,permissions
from rest_framework import status
from .serlizers import(
  SignUpSerializer ,
  LoginSerlizer,
  ForgetPasswordSerializer,
  VerifyResetPasswordOtPSerializer,
  VerifyEmailSerializer,
  resendverifySerializer,
  ResetPasswordSerializers
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
from .service import *
from rest_framework_simplejwt.token_blacklist.models import  OutstandingToken, BlacklistedToken
from ..models import PasswordResetToken
from .serlizers import GoogleAuthSerializers
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
User=get_user_model()

#! signup

class SignUp(generics.CreateAPIView):

    permission_classes=[permissions.AllowAny]
    serializer_class= SignUpSerializer
    @method_decorator(ratelimit(key='ip', rate='3/m',method='POST'))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully. Please verify your email to continue."},
            status=status.HTTP_201_CREATED
        )
#! Login

class LoginView(APIView):
    
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='3/m',method='POST'))
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
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m',method='GET'))
    def post(self,request):
        ser= VerifyEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        otp=ser.validated_data['otp']
        hash_otp= hashlib.sha256(otp.encode()).hexdigest()
        email=ser.validated_data['email']
        with transaction.atomic():
          
            Emailotp = Emailverifiction.objects.select_for_update().filter(
                user__email=email,
            ).first()
          
            if not Emailotp:
                return Response({"message": "This OTP has expired. Please request a new one."},status.HTTP_400_BAD_REQUEST)
            if Emailotp.is_expire():
                return Response({
                    "message": "This OTP has expired. Please request a new one."
                },status.HTTP_400_BAD_REQUEST)
            if Emailotp.attempts >=3:
                return Response({
                    "message": "Too many invalid attempts. Please request a new OTP."
                },status.HTTP_400_BAD_REQUEST)
            if hash_otp!=Emailotp.otp:
                Emailotp.attempts+=1
                Emailotp.save(update_fields=['attempts'])
                return Response({
                    "message": "Invalid OTP entered. Please try again."
                },status.HTTP_400_BAD_REQUEST)
           
            Emailotp.user.is_verify = True
            Emailotp.used_it = True
            Emailotp.user.save(update_fields=["is_verify"])
            Emailotp.save(update_fields=["used_it"])
            Emailotp.delete()
            
            refresh = RefreshToken.for_user(Emailotp.user)
            
            return Response({
                "message": "Your email is verified. Welcome!",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }
            }, status=status.HTTP_200_OK)
         

      
    

#! resend verify email
class ResendVerifyEmailView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        ser=resendverifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email=ser.validated_data['email']
        user= User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({
                "message": "If an account with this email exists, then check you email."
            },status=status.HTTP_200_OK)
        
        if user.is_verify:
            return Response({
                "message": "This email is already verified."
            },status=status.HTTP_200_OK)
        
        from .task import send_verification_email
        send_verification_email.delay(id=str(user.id))
        
        return Response({
            "message": "A new OTP has been sent to your email."
        },status=status.HTTP_200_OK)
            

    
        
        
#! forget password endpoint
from .task import send_reset_password_email
class SendForgetPassworEmaildView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        ser=ForgetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user= User.objects.filter(email__iexact=ser.validated_data['email']).first()
        if user:
            send_reset_password_email.delay(id=str(user.id))
        return Response({
            "message": "If an account exists, a password reset OTP has been sent to your email."
        },status=status.HTTP_200_OK)
        
#! reset password endpoint
class VerifyResetPasswordOtpView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        
        ser=VerifyResetPasswordOtPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email=ser.validated_data['email']
        otp=ser.validated_data['otp']
        hash_otp= hashlib.sha256(otp.encode()).hexdigest()
        with transaction.atomic():    

            Emailotp= Emailverifiction.objects.select_for_update().filter(
                user__email=email
            ).first()
            if not Emailotp:
                return Response({"message": "This OTP has expired. Please request a new one."},status.HTTP_400_BAD_REQUEST)
                
            if Emailotp.is_expire():
                return Response({
                "message": "This OTP has expired. Please request a new one."
                },status.HTTP_400_BAD_REQUEST)
            if Emailotp.attempts >=3:
                return Response({
                    "message": "Too many invalid attempts. Please request a new OTP."
                },status.HTTP_400_BAD_REQUEST)
            if hash_otp!=Emailotp.otp:
                Emailotp.attempts+=1
                Emailotp.save(update_fields=['attempts'])
                return Response({
                    "message": "Invalid OTP entered. Please try again."
                    },status.HTTP_400_BAD_REQUEST)
                
            Emailotp.used_it = True
            Emailotp.save(update_fields=["used_it"])
            token= gernate_password_token(Emailotp.user)
            Emailotp.delete()
        
        return Response({
            "message": "Email verified successfully.",
            "token":token,
        },status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes=[permissions.AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        ser= ResetPasswordSerializers(data=request.data)
        ser.is_valid(raise_exception=True)
        password=ser.validated_data['password']
        token=ser.validated_data['token']
        token_hash=hashlib.sha256(token.encode()).hexdigest()
        tokenobj=PasswordResetToken.objects.filter(token=token_hash).first()
        if not tokenobj:
            return Response({"message":"invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        if tokenobj.is_expired() or tokenobj.used_it:
            return Response({
                "message": "This password reset session has expired. Please restart the process."
            },status.HTTP_400_BAD_REQUEST)
            
        if token_hash!=tokenobj.token:
            return Response({
                "message": "Invalid or manipulated reset token. Please restart the process."
            },status.HTTP_400_BAD_REQUEST)
        tokenobj.user.set_password(password)
        tokenobj.user.save(update_fields=['password'])
        tokenobj.used_it=True
        tokenobj.save(update_fields=['used_it'])
        tokens= OutstandingToken.objects.filter(user=tokenobj.user)
        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({
            "message":"password reset successfully"
        },status.HTTP_200_OK)
        
            
        
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
            return Response({"error": "Failed to logout. Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
class GoogleLoginAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        
        ser=GoogleAuthSerializers(data=request.data)
        ser.is_valid(raise_exception=True)
        token=ser.validated_data['token']
        try:
            idinfo= id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            email=idinfo['email']
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'is_verify': True,
                    }
                )
                if created:
                    user.set_unusable_password() 
                    user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login Successful",
                    "is_new_user": created,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    }
                },status.HTTP_200_OK)
                
            
            
        except ValueError:
            return Response({"error": "Invalid or expired Google token"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            
        
    