from rest_framework import serializers
from  django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from ..models import Emailverifiction
from .task import send_verification_email
from django.contrib.auth import authenticate
User= get_user_model()
from django.core.validators import validate_email
class SignUpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields=("email","password")
         
    def create(self, validated_data):
        user= User.objects.create_user(
            email= validated_data['email'],
            password=validated_data['password'],
        )
        send_verification_email.delay(id=str(user.id))
            
        return user
    def validate_password(self,value):
        validate_password(value)
        return value
    
    
class LoginSerlizer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.is_verify:
            raise serializers.ValidationError("Email not verified first verify your email")
        
        attrs['user'] = user
        return attrs
    
    
class VerifyEmailSerializer(serializers.Serializer):
    otp=serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
    
    def validate_otp(self,value):
        if not value:
            raise serializers.ValidationError('otp is required')
        if len(value)>6 or len(value)<6:
            raise serializers.ValidationError('check your otp length')
        return value


class ForgetPasswordSerializer(serializers.Serializer):
    email=serializers.EmailField(write_only=True)
    
    
class resendverifySerializer(serializers.Serializer):
    email=serializers.EmailField(write_only=True)
    
    
        
        
class ResetPasswordSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    otp=serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate_password(self, value):
        validate_password(value)
        return value
    def validate_otp(self,value):
        if not value:
            raise serializers.ValidationError('otp is required')
        if len(value)>6 or len(value)<6:
            raise serializers.ValidationError('check your otp length')
        return value