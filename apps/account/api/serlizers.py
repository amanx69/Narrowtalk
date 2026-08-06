from rest_framework import serializers
from  django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from ..models import Emailverifiction
from .task import send_verification_email
from django.contrib.auth import authenticate
User= get_user_model()
class SignUpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields=("email","password")
         
    def create(self, validated_data):
        
        user= User.objects.create_user(
            email= validated_data['email'],
            password=validated_data['password'],
            
        )
        send_verification_email.delay(id=user.id)
            
        return user

    def validate_email(self,value):
        if User.objects.filter(email=value):
            raise serializers.ValidationError("email already exites")
        return value
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
            raise serializers.ValidationError("Email not verified")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        
        attrs['user'] = user
        return attrs
    
    
        