# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f"notifications_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        @database_sync_to_async
        def get_initial_data():
            unread_count = user.notifications.filter(is_read=False).count()
            username = user.username
            return unread_count, username

        count, username = await get_initial_data()
        await self.send(text_data=json.dumps({
            "type":         "unread_count",
            "unread_count": count,
            "username":     username,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "mark_read":
            notif_id = data.get("notification_id")

            @database_sync_to_async
            def mark_read():
                Notification.objects.filter(
                    id        = notif_id,
                    recipient = self.scope["user"]
                ).update(is_read=True)

            await mark_read()
            await self.send(text_data=json.dumps({
                "type":            "marked_read",
                "notification_id": notif_id,
            }))

    # server se notification aaya → client ko bhejo
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type":        "notification",
            "id":          event.get("id"),
            "notif_type":  event["notif_type"],
            "title":       event["title"],
            "body":        event["body"],
            "project_id":  event.get("project_id"),
            "post_id":     event.get("post_id"),
            "sender_name": event.get("sender_name"),
            "is_read":     event.get("is_read", False),
            "created_at":  event.get("created_at"),
        }))