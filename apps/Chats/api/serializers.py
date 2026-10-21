from rest_framework import serializers
from ..models import ChatGroup ,Message ,GroupMember
from apps.Profile.api.serializer import ChatProfileSerializer ,MemebrProfileSerializer
from core.helpers import (
    CompressedProfilePicField,
    CompressedMediaFileField,
    get_cloudinary_thumbnail,
)

class ChatGroupeListSerializer(serializers.ModelSerializer):
    group_dp = CompressedProfilePicField(required=False)
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = (
            'id',
            'group_name',
            'group_dp',
            'last_message',
            'last_message_time',
            'last_message_sender',
            'unread_count',
        )

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if not last_msg:
            return None
        if last_msg.text:
            return last_msg.text
        if last_msg.file:
            return "📎 Media"
        return ""

    def get_last_message_time(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return last_msg.created_at.isoformat() if last_msg else None

    def get_last_message_sender(self, obj):
        last_msg = obj.messages.select_related('sender__user_profile').order_by('-created_at').first()
        if not last_msg or not last_msg.sender:
            return None
        profile = getattr(last_msg.sender, 'user_profile', None)
        if profile and profile.username:
            return profile.username.strip()
        return last_msg.sender.username or "Member"

    def get_unread_count(self, obj):
        return 0


CompressedFileField = CompressedMediaFileField # change ser name for simplicty
          
class MessageSerilizer(serializers.ModelSerializer):
    sender_profile = ChatProfileSerializer(source='sender.user_profile', read_only=True)
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'text', 'created_at', 'sender_profile', 'sender', 'reactions')
        read_only_fields = ('id', 'created_at', 'sender', 'sender_profile', 'reactions')

    def get_reactions(self, obj):
        try:
            reactions_qs = getattr(obj, 'reactions', None)
            if reactions_qs is None:
                return []
            all_reactions = reactions_qs.all()
            if not all_reactions:
                return []
            result = {}
            for r in all_reactions:
                if r.emoji not in result:
                    result[r.emoji] = {'emoji': r.emoji, 'count': 0, 'user_ids': []}
                result[r.emoji]['count'] += 1
                result[r.emoji]['user_ids'].append(str(r.user_id))
            return list(result.values())
        except Exception:
            return []

    def validate_file(self, value):
        if value:
            max_size = 50 * 1024 * 1024  # 50 MB
            if value.size > max_size:
                raise serializers.ValidationError("File size must not exceed 50MB.")
        return value


class GroupMemberListSerilizer(serializers.ModelSerializer):
    user_profile = MemebrProfileSerializer(source='user.user_profile', read_only=True)
    class Meta:
        model = GroupMember
        fields = ('user', 'is_active', 'role', 'joined_at', 'user_profile')


class GroupMediaSerializer(serializers.ModelSerializer):
    file = CompressedFileField(read_only=True)
    thumbnail = serializers.SerializerMethodField()
    media_type = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'file', 'thumbnail', 'media_type', 'created_at')

    def get_thumbnail(self, obj):
        if not obj.file:
            return None
        url = getattr(obj.file, 'url', None) or str(obj.file)
        return get_cloudinary_thumbnail(url)

    def get_media_type(self, obj):
        if not obj.file:
            return "text"
        name = (getattr(obj.file, 'name', '') or '').lower()
        video_exts = ('.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.m4v', '.3gp', '.wmv', '.ts')
        if any(name.endswith(ext) for ext in video_exts):
            return "video"
        image_exts = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.svg')
        if any(name.endswith(ext) for ext in image_exts):
            return "image"
        return "document"


    
    