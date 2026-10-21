import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, GroupMember
from django.contrib.auth import get_user_model


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

            # Handle emoji reactions
            action = incoming_data.get('action')
            if action == 'reaction':
                message_id = incoming_data.get('message_id')
                emoji = incoming_data.get('emoji', '').strip()
                if not message_id or not emoji:
                    return

                reaction_result = await self.toggle_reaction(message_id, emoji)
                if reaction_result:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_reaction',
                            'message_id': str(message_id),
                            'emoji': emoji,
                            'user_id': str(self.user.id),
                            'action': reaction_result['action'],
                            'reactions': reaction_result['reactions'],
                        }
                    )
                return

            chat_text = incoming_data.get('message', '').strip()

            if not chat_text:
                return 

            new_msg = await self.save_message(chat_text)

            profile_username = await self.get_profile_username()
            profile_pic = await self.get_profile_pic()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': str(new_msg.id),
                    'message': chat_text,
                    'sender': profile_username,
                    'user_id': str(self.user.id), 
                    'profile_pic': profile_pic,
                    'created_at': new_msg.created_at.isoformat()
                }
            )

            # Real-time notification dispatch to active group members
            await self.dispatch_chat_notifications(chat_text, profile_username)

        except json.JSONDecodeError:

            await self.send(text_data=json.dumps({
                'error': 'Invalid format. Send proper JSON.'
            }))
        except Exception as err:
            import logging
            logging.error(f"WebSocket Receive Error: {err}")
            await self.send(text_data=json.dumps({
                'error': 'An internal error occurred.'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'sender': event['sender'],
            'user_id': event.get('user_id'), 
            'profile_pic': event.get('profile_pic'),
            'created_at': event['created_at']
        }))

    async def chat_reaction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'emoji': event['emoji'],
            'user_id': event['user_id'],
            'action': event['action'],
            'reactions': event['reactions'],
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

    @database_sync_to_async
    def get_profile_username(self):
        try:
            return self.user.user_profile.username
        except Exception:
            return self.user.email.split('@')[0] if hasattr(self.user, 'email') else "User"
    
    @database_sync_to_async
    def get_profile_pic(self):
        try:
            return self.user.user_profile.profile_pic.url
        except Exception:
            return None

    @database_sync_to_async
    def toggle_reaction(self, message_id, emoji):
        from .models import MessageReaction, Message
        try:
            msg = Message.objects.get(id=message_id, group_id=self.group_id)
            existing = MessageReaction.objects.filter(message=msg, user=self.user).first()
            if existing:
                if existing.emoji == emoji:
                    # Tapped the exact same emoji -> toggle remove
                    existing.delete()
                    action = 'removed'
                else:
                    # Tapped a different emoji -> replace old reaction with new one
                    existing.emoji = emoji
                    existing.save(update_fields=['emoji'])
                    action = 'replaced'
            else:
                MessageReaction.objects.create(message=msg, user=self.user, emoji=emoji)
                action = 'added'

            # Aggregate reactions for this message
            all_r = MessageReaction.objects.filter(message=msg)
            grouped = {}
            for r in all_r:
                if r.emoji not in grouped:
                    grouped[r.emoji] = {'emoji': r.emoji, 'count': 0, 'user_ids': []}
                grouped[r.emoji]['count'] += 1
                grouped[r.emoji]['user_ids'].append(str(r.user_id))

            return {
                'action': action,
                'reactions': list(grouped.values()),
            }
        except Exception as e:
            import logging
            logging.error(f"Toggle reaction error: {e}")
            return None

    @database_sync_to_async
    def get_recipient_members_info(self):
        from .models import ChatGroup, GroupMember
        try:
            group = ChatGroup.objects.select_related('project').get(id=self.group_id)
            members = list(
                GroupMember.objects.filter(
                    chat_group_id=self.group_id,
                    is_active=True
                ).exclude(user=self.user).values_list('user_id', flat=True)
            )
            project_id = str(group.project.id) if group.project else None
            group_name = group.group_name or (group.project.project_name if group.project else "Project Chat")
            return members, project_id, group_name
        except Exception as e:
            import logging
            logging.error(f"Error fetching group members for notification: {e}")
            return [], None, "Project Chat"

    async def dispatch_chat_notifications(self, text, sender_name):
        try:
            from apps.notification.api.service import notify
            member_ids, project_id, group_name = await self.get_recipient_members_info()
            preview = (text[:60] + "...") if len(text) > 60 else text

            for member_id in member_ids:
                notify.delay(
                    recipient_id=str(member_id),
                    sender_id=str(self.user.id),
                    notif_type="new_message",
                    title=f"New message in {group_name}",
                    body=f"{sender_name}: {preview}",
                    project_id=project_id,
                )
        except Exception as e:
            import logging
            logging.error(f"Chat notification dispatch error: {e}")
