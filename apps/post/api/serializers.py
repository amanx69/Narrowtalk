from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.Profile.models import Skill
from ..models import Project, RoleNeeded ,Application,Membership
from apps.Profile.api.serializer import SkillSerializer ,MemebrProfileSerializer ,ApplictionProfileSerializer ,ProjectProfileSerializer,RequestProfileSerializer    
from ..models import RequestJoinProjet

#! this ser used for create only create the project

from core.helpers import CompressedMediaFileField

CompressedProjectFileField = CompressedMediaFileField
          
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id","title",'project_name', "description", "stage", "created_at",'like_count','comment_count','save_count','project_file','status','github_link')
        read_only_fields = ('id', 'created_at', 'like_count', 'comment_count', 'save_count', 'status')

    def validate_github_link(self, value):
        if not value:
            return value
        val = value.strip()
        if not (val.startswith('https://github.com/') or val.startswith('http://github.com/')):
            raise serializers.ValidationError("Please provide a valid GitHub URL (e.g. https://github.com/username/repo).")
        return val

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace only.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        if len(value) > 300:
            raise serializers.ValidationError("Title must not exceed 300 characters.")
        return value.strip()
    def validate_project_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty or whitespace only.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Project name must be at least 3 characters long.")
        if len(value) > 50:
            raise serializers.ValidationError("Project name must not exceed 50 characters.")
        return value.strip()

    def validate_description(self, value):
       
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty or whitespace only.")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value.strip()

    def validate_stage(self, value):
        valid_stages = [choice[0] for choice in Project.Stage.choices]
        if value not in valid_stages:
            raise serializers.ValidationError(f"Stage must be one of: {', '.join(valid_stages)}")
        return value
 
    def validate_project_file(self, value):
        if not value:
            return value
            
        allowed_types = [
            'image/jpeg', 'image/png', 'image/webp',  # Images
            'video/mp4', 'video/webm',                # Videos
            'application/pdf'                         # PDF
        ]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPG/PNG images, MP4/WEBM videos, and PDFs are allowed.")
        
        # Cloudinary enforces a 10MB limit for raw files and images
        if value.content_type.startswith('video/'):
            max_size = 50 * 1024 * 1024  
            if value.size > max_size:
                raise serializers.ValidationError("Video size must be under 50MB.")
        else:
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError("Image or PDF size must be under 10MB.")
        return value
 # this ser used for only in profile project listing 
class ProjectListSerializer(serializers.ModelSerializer):
    owner=ProjectProfileSerializer(source='owner.user_profile')
    project_file = CompressedProjectFileField(read_only=True)
    class Meta:
        model=Project #! think about show like in project detail
        fields=('id','project_name',"title","description",'stage','created_at','owner','project_file','status','like_count','save_count','comment_count','view_count','github_link')
        read_only_fields=fields   

#! this ser is used for current user projects with application counts & details for manage appliction screen 
# and help to see project role appliction
class CurrentUserProjectListSerializer(serializers.ModelSerializer):
    owner = ProjectProfileSerializer(source='owner.user_profile', read_only=True)
    application_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Project
        fields = (
            'id',
            'project_name',
            'title',
            'description',
            'stage',
            'status',
            'created_at',
            'owner',
            'application_count',
            'like_count',      
            'save_count',      
            'comment_count',  
            'view_count', 
            'github_link',
        )
        read_only_fields = fields
#! this ser used for get Project detiles project and used everywere where nedd to show detiles

class ProjectDetailSerializer(serializers.ModelSerializer):
    owner = ProjectProfileSerializer(source='owner.user_profile')
    chat_group_id = serializers.SerializerMethodField()
    project_file = CompressedProjectFileField(read_only=True)

    class Meta:
        model = Project #! think about show like in project detail
        fields = ('id', 'project_name', "title", 'project_file', "description", 'stage', 'created_at', 'owner', 'like_count', 'save_count', 'comment_count', 'view_count', 'status', 'chat_group_id', 'github_link')
        read_only_fields = fields

    def get_chat_group_id(self, obj):
        try:
            return str(obj.chat_group.id) if hasattr(obj, 'chat_group') and obj.chat_group else None
        except Exception:
            return None
    
        

#! this ser user for give project owner role list
#  and used in where user apply (ex:home apply feed apply and other user profile)
class GetJobRoleSerializer(serializers.ModelSerializer):
    required_skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = RoleNeeded
        fields = ("id", "project", "title", "description", "slots_available", "required_skills", "is_open", "created_at","role","is_complete",'application_count')

#! this ser used for create a role
class CreateJobRoleSerializer(serializers.ModelSerializer):
    required_skills = SkillSerializer(
        many=True,
        write_only=True,
        required=True
    )

    class Meta:
        model = RoleNeeded
        fields = ("title", "description", "slots_available", "required_skills", "is_open",'role')

    def validate_title(self, value):
        """Validate role title is not empty and reasonable length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Role title cannot be empty.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Role title must be at least 2 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Role title must not exceed 100 characters.")
        return value.strip()

    def validate_description(self, value):
        """Validate description if provided."""
        if not value:
            raise serializers.ValidationError("description must be included")
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Description must be at least 5 characters long.")
        return value

    def validate_slots_available(self, value):
        """Validate slots_available is a positive integer."""
        if value is None or value < 1:
            raise serializers.ValidationError("Slots available must be at least 1.")
        if value > 100:
            raise serializers.ValidationError("Slots available cannot exceed 100.")
        return value

  

    def create(self, validated_data):
        skills_data = validated_data.pop("required_skills", [])
        role = RoleNeeded.objects.create(**validated_data)
        skill_objs = []
        for s in skills_data:
            name = s.get("name", "").strip()
            if name:
                skill,_ = Skill.objects.get_or_create(name=name)
                skill_objs.append(skill)
        if skill_objs:
            role.required_skills.set(skill_objs)
        return role
    
    
    def update(self, instance, validated_data):
        skills_data = validated_data.pop("required_skills", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if skills_data is not None:
            skill_objs = []
            for skill in skills_data:
                name = skill.get("name", "").strip()
                if name :
                    skill_obj,_= Skill.objects.get_or_create(name=name)
                    skill_objs.append(skill_obj)
            if skill_objs:
                instance.required_skills.set(skill_objs)
            else:
                instance.required_skills.clear()

        return instance
     
     
     
     
#! this ser used for create a appliction
class ApplictionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Application
        fields=("id",'message','status','github_link','portfolio_link','project_link')
        read_only_fields = ('id', 'status')

    def validate_message(self, value):
        
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        if value and len(value) > 1000:
            raise serializers.ValidationError("Message must not exceed 1000 characters.")
        return value.strip() if value else value

   
    def validate(self, data):

        message = data.get('message', '').strip() if data.get('message') else ''
        
        
        if not message :
            raise serializers.ValidationError("message purpose must be provided.")
        
        return data

    def create(self, validated_data):
        user=self.context['request'].user
        apply_role=self.context['roles']
        print(apply_role)
        appliction=Application.objects.create(apply_role_purpose=apply_role,user=user,**validated_data)
        return appliction
        
#! this ser used for project owner appliction list
class GetapplictionSerializar(serializers.ModelSerializer):
    applied_user= ApplictionProfileSerializer(source='user.user_profile',read_only=True)
    class Meta:
        model=Application 
        fields=('id','message','apply_role_purpose','status','created_at','applied_user','user')
        read_only_fields=fields    
    
class GetapplictionDetileSerializar(serializers.ModelSerializer):
    applied_user= ApplictionProfileSerializer(source='user.user_profile',read_only=True)
    class Meta:
        model=Application 
        fields=('message','apply_role_purpose','status','created_at','github_link','portfolio_link','project_link','applied_user','user')
        read_only_fields=fields    
    
    
    
#! this ser used for project owner list of his memebrs
class MemebrSerializer(serializers.ModelSerializer):
    user= MemebrProfileSerializer(source='user.user_profile',read_only=True)
    user_id=serializers.UUIDField(source="user.id",read_only=True)
    
    class Meta:
        model=Membership
        fields=('id','role_title','joined_at','is_active','user','user_id')
        
     
        
'''
this all ser handle applied user list of appliction
and how many i join project
'''

class AppliedApplictionDetilesSerializer(serializers.ModelSerializer):
    role= GetJobRoleSerializer(read_only=True)
    project_name=serializers.CharField(source='role.project.project_name', read_only=True)
    project_owner= ApplictionProfileSerializer(source='role.project.owner.user_profile',read_only=True) #! this er return project owner
    class Meta:
        model=Application
        fields=('id','message','apply_role_purpose','status','created_at','github_link','portfolio_link','role','project_name','project_owner',)

class AppliedApplictionListSerializer(serializers.ModelSerializer):
    project_name=serializers.CharField(source='role.project.project_name', read_only=True)
    role_title = serializers.CharField(source='role.title', read_only=True)
    project_owner= ApplictionProfileSerializer(source='role.project.owner.user_profile',read_only=True) #! this er return project owner
    class Meta:
        model=Application
        fields=('id','message','apply_role_purpose','status','created_at','project_name', 'role_title',"project_owner")

          
class ProjectJoinSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    class Meta:
        model = Membership
        fields = ('is_active', 'role_title', 'joined_at', 'project', 'project_name')







''' this all serializers used for request and join feathures'''

class SentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=RequestJoinProjet
        fields=('id','created_at',"message","receiver_user",'project','role','status')
        read_only_fields = ['id', 'created_at', 'status']
        
        
    def validate(self, attrs):
        user = self.context["request"].user
        project = attrs["project"]
        receiver = attrs["receiver_user"]
        role = attrs["role"]

        if not user:
            raise serializers.ValidationError('user not found')
        if project.owner != user:
            raise serializers.ValidationError("You are not the owner of this project.")
        if role.project_id != project.id:
            raise serializers.ValidationError("This role does not belong to this project.")
        if receiver == user:
            raise serializers.ValidationError("You cannot send a request to yourself.")
        # Check if a pending request already exists for this user in this project
        if RequestJoinProjet.objects.filter(project=project,receiver_user=receiver,status=RequestJoinProjet.Status.PENDING).exists():
            raise serializers.ValidationError('you only send one request in one project')
            
        if Membership.objects.filter(user=receiver, project=project, is_active=True).exists():
            raise serializers.ValidationError("This user is already an active member of the project.")

        return attrs


class ProjectNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'project_name')
        read_only_fields = fields

class GetRequestJoinProjectListSerializer(serializers.ModelSerializer):
    
    request_owner_profile= RequestProfileSerializer(source='request_owner.user_profile', read_only=True)
    role= serializers.CharField(source='role.role',read_only=True)
    project__name=serializers.CharField(source='project.project_name', read_only=True)
    project_id=serializers.CharField(source='project.id', read_only=True)
    class Meta:
        model= RequestJoinProjet
        fields=('id',"project_id","project__name",'role','request_owner_profile','message','status','created_at')
        read_only_fields=fields
        
        

class GetRequestJoinProjectDetailSerializer(serializers.ModelSerializer):
    project= ProjectDetailSerializer(read_only=True)
    role= GetJobRoleSerializer(read_only=True)
    profile=RequestProfileSerializer(source='request_owner.user_profile')
    class Meta:
        model=RequestJoinProjet
        fields=("id",'project','profile','role','message','status','created_at')

# send req ser list and detiles
class SentRequestJoinProjectListSerializer(serializers.ModelSerializer):
    receiver_user_profile = RequestProfileSerializer(source='receiver_user.user_profile', read_only=True)
    role= serializers.CharField(source='role.role',read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    project_id = serializers.CharField(source='project.id', read_only=True)
    
    class Meta:
        model = RequestJoinProjet
        fields = ('id', 'project_id', 'project_name', 'role', 'receiver_user_profile', 'status', 'message', 'created_at')

class SentRequestJoinProjectDetailSerializer(serializers.ModelSerializer):
    project = ProjectDetailSerializer(read_only=True)
    role = GetJobRoleSerializer(read_only=True)
    profile = RequestProfileSerializer(source='receiver_user.user_profile', read_only=True)
    
    class Meta:
        model = RequestJoinProjet
        fields = ("id", 'project', 'profile', 'role', 'message', 'status', 'created_at')