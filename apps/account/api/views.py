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
from django.db import transaction

User=get_user_model()
#! signup

class SignUp(generics.CreateAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class= SignUpSerializer
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def create(self, request, *args, **kwargs):
        print(*args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if not user.is_verify:
            return Response({"message": "Please verify your email before logging in."}, status=status.HTTP_201_CREATED)
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
        with transaction.atomic():
            EmailToken = get_object_or_404(
                Emailverifiction.objects.select_for_update(),
                token_hash=token,
                purpose="VERIFY",
            )
            if EmailToken.is_expire() or EmailToken.used_it:
                return Response({
                    "message":"your token is expire resent again",
                },status=status.HTTP_400_BAD_REQUEST)

            EmailToken.user.is_verify = True
            EmailToken.used_it = True
            EmailToken.user.save(update_fields=["is_verify"])
            EmailToken.save(update_fields=["used_it"])

        return Response({
            "message":"email verify compleated"
        },status=status.HTTP_200_OK )
        
        
#! forget password endpoint
class SendForgetPassworEmaildView(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request):
        email= request.data.get('email')
        if not email:
            return Response({
                "message":"email is required"
            },status=status.HTTP_400_BAD_REQUEST)
        user= User.objects.filter(email=email).first()
        if not user:
            return Response({
                "message":"user not found"
            },status=status.HTTP_404_NOT_FOUND)
        
        from .task import send_reset_password_email
        send_reset_password_email.delay(id=str(user.id))
        
        return Response({
            "message":"reset password email send"
        },status=status.HTTP_200_OK)
        
#! reset password endpoint
class ResetPasswordView(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m',method='POST'))
    def post(self,request,token):
        with transaction.atomic():
            EmailToken = get_object_or_404(
                Emailverifiction.objects.select_for_update(),
                token_hash=token,
                purpose="RESETPASSWORD",
            )
            if EmailToken.is_expire() or EmailToken.used_it:
                return Response({
                    "message":"your token is expire resent again",
                },status=status.HTTP_400_BAD_REQUEST)

            password = request.data.get('password')
            if not password:
                return Response({
                    "message":"password is required"
                },status=status.HTTP_400_BAD_REQUEST)

            EmailToken.user.set_password(password)
            EmailToken.user.save(update_fields=["password"])
            EmailToken.used_it = True
            EmailToken.save(update_fields=["used_it"])
        
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
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)