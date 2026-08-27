# serializer.py
from rest_framework import serializers
from ..models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model  = Notification
        fields = [
            "id",
            "notif_type",
            "title",
            "body",
            "is_read",
            "sender",
            "sender_name",
            "project",
            "post",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_sender_name(self, obj):
        if obj.sender:
            return obj.sender.username
        return "System"

    def get_post(self, obj):
        if obj.project:
            return {
                "id": str(obj.project.id),
                "title": obj.project.title,
                "stage": obj.project.stage,
            }
        return None