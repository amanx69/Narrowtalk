import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from ..models import RoomParticipant
from .serializer import MemberSerlizer

User = get_user_model()


class RoomConsumer(AsyncWebsocketConsumer):
    """Realtime room socket.

    URL: ws://<host>/ws/room/<room_id>/?token=<access_token>

    Events sent to the client:
      - participants.update : current participant list (on join + on broadcast)
      - kicked               : sent to the removed member (owner kicked them)
      - room.deleted         : sent to everyone when the owner deletes the room
    """

    async def connect(self):
        self.user = await self._get_user()
        if self.user is None:
            await self.close(code=4001)
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"room_{self.room_id}"
        self.user_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

        await self.send_room_participants()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Clients can ask for a fresh participant list at any time.
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return
        if data.get("type") == "participants.request":
            await self.send_room_participants()

    # ── group handlers ─────────────────────────────────────────────
    async def room_participants_update(self, event):
        await self.send_room_participants()

    async def room_kicked(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "kicked",
                    "room_id": str(self.room_id),
                    "room_name": event.get("room_name", ""),
                    "message": event.get(
                        "message", "You were kicked by the owner"
                    ),
                }
            )
        )

    async def room_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "room.deleted",
                    "room_id": str(self.room_id),
                    "room_name": event.get("room_name", ""),
                    "message": event.get(
                        "message", "Room was deleted by the owner"
                    ),
                }
            )
        )

    # ── helpers ────────────────────────────────────────────────────
    async def send_room_participants(self):
        participants = await sync_to_async(
            lambda: list(
                RoomParticipant.objects.filter(room_id=self.room_id)
                .select_related("user", "user__user_profile")
                .order_by("joined_at")
            )
        )()
        data = await sync_to_async(
            lambda: MemberSerlizer(participants, many=True).data
        )()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "participants.update",
                    "room_id": str(self.room_id),
                    "participants": data,
                }
            )
        )

    async def _get_user(self):
        query = self.scope.get("query_string", b"").decode()
        token = parse_qs(query).get("token", [None])[0]
        if not token:
            return None
        try:
            access = AccessToken(token)
            return await User.objects.aget(id=access["user_id"])
        except Exception:
            return None
