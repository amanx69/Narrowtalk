from rest_framework import serializers
from ..models import UserBlock,Report
from apps.post.models import Project
from apps.Chats.models import ChatGroup
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
User=get_user_model()

class BlokUserSerializers(serializers.ModelSerializer):#TODO remove it later 
    
    class Meta:
        model=UserBlock
        fields=('created_at','blocker','blocked_user')
        
        
 
        
      
      
class ReportSerializer(serializers.ModelSerializer):
    reported_project = serializers.UUIDField(required=False, allow_null=True)
    reported_user = serializers.UUIDField(required=False, allow_null=True)
    reported_group = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Report
        fields = ('id', 'reason', 'description', 'status', 'created_at', 'reported_project', 'reporter', 'reported_user', 'reported_group')
        read_only_fields = ('status', 'reporter', 'id', 'created_at')
        
        
    def validate_reported_project(self, project_id):
        if project_id:
           return get_object_or_404(Project, id=project_id)
        return None
    
    def validate_reported_user(self, user_id):
        if user_id:
            if self.context['request'].user.id == user_id:
                raise ValidationError("You cannot report yourself.")
            return get_object_or_404(User, id=user_id)
        return None
    
    def validate_reported_group(self, group_id):
        if group_id:
            return get_object_or_404(ChatGroup, id=group_id)
        return None
    
    def validate(self, attrs):
        user = attrs.get('reported_user')
        project = attrs.get('reported_project')
        group = attrs.get('reported_group')
        
        reported_count = sum(1 for item in (user, project, group) if item is not None)
        
        if reported_count == 0:
            raise ValidationError("You must report a user, project, or group.")
            
        if reported_count > 1:
            raise ValidationError("You can only report one target at a time.")
            
        return attrs
        
        