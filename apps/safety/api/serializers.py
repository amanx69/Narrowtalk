from rest_framework import serializers
from ..models import UserBlock,Report
from apps.post.models import Project
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
User=get_user_model()

class BlokUserSerializers(serializers.ModelSerializer):#TODO remove it later 
    
    class Meta:
        model=UserBlock
        fields=('created_at','blocker','blocked_user')
        
        
 
        
      
      
class ReportSerializer(serializers.ModelSerializer):
    reported_project=serializers.UUIDField(required=False)
    reported_user=serializers.UUIDField(required=False)
    
    class Meta:
        model= Report
        fields=('reason','description','status','created_at','reported_project','reporter','reported_user')
        read_only_fields = ('status', 'reporter', 'id', 'created_at')
        
        
    def validate_reported_project(self, project_id):
        if project_id:
           return get_object_or_404(Project,id=project_id)
        return None
    
    def validate_reported_user(self,user_id):
        if user_id:
            if self.context['request'].user.id == user_id:
                raise ValidationError("You cannot report yourself.")
            return get_object_or_404(User,id=user_id)
        return  None
    
    def validate(self, attrs):
        user = attrs.get('reported_user')
        project = attrs.get('reported_project')
        
        if not user and not project:
            raise ValidationError("You must report either a user or a project.")
            
        if user and project:
            raise ValidationError("You can only report one thing at a time (either a user or a project).")
            
        return attrs
        
        