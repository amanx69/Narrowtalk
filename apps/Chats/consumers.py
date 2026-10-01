import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, GroupMember
from django.contrib.auth import get_user_model

# User model nikalna
CustomUser = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
   
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'chat_{self.group_id}'
        self.user = self.scope.get('user')

     
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return


        is_active_member = await self.check_is_member()
        if not is_active_member:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
      
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
  
        try:
            incoming_data = json.loads(text_data)
            chat_text = incoming_data.get('message', '').strip()

            if not chat_text:
                return 

  
            new_msg = await self.save_message(chat_text)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': str(new_msg.id),
                    'message': chat_text,
                    'sender': self.user.username,
                    'created_at': new_msg.created_at.isoformat()
                }
            )

        except json.JSONDecodeError:

            await self.send(text_data=json.dumps({
                'error': 'Invalid format. Send proper JSON.'
            }))
        except Exception as err:
      
            await self.send(text_data=json.dumps({
                'error': 'An internal error occurred.'
            }))

    async def chat_message(self, event):
  
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'sender': event['sender'],
            'created_at': event['created_at']
        }))


    @database_sync_to_async
    def check_is_member(self):
        try:
            return GroupMember.objects.filter(
                chat_group_id=self.group_id, 
                user=self.user,
                is_active=True
            ).exists()
        except Exception:
            return False

    @database_sync_to_async
    def save_message(self, text_content):
        return Message.objects.create(
            group_id=self.group_id,
            sender=self.user,
            text=text_content
        )