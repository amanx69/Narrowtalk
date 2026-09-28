from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.post.models import Project
from apps.Chats.models import ChatGroup, GroupMember, Message

User = get_user_model()

class ChatAPITestCase(APITestCase):
    def setUp(self):

        self.owner = User.objects.create_user(email="owner@test.com", password="password123")
        self.member = User.objects.create_user(email="member@test.com", password="password123")
        self.hacker = User.objects.create_user(email="hacker@test.com", password="password123")


        self.project = Project.objects.create(
            owner=self.owner,
            project_name="Test Project",
            title="Test Project Title",
            description="Testing"
        )

        self.chat_group = ChatGroup.objects.get(project=self.project)
        
  
        GroupMember.objects.create(
            chat_group=self.chat_group,
            user=self.member,
            role=GroupMember.ChatRole.MEMBER
        )


        self.message = Message.objects.create(
            group=self.chat_group,
            sender=self.member,
            text="Hello testing!"
        )

    def test_chat_list_view(self):

        self.client.force_authenticate(user=self.member)
        url = reverse('v1:groupe-list') 
        response = self.client.get(url)
        print(response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_chat_list_view_anoun(self):
        url = reverse('v1:groupe-list') 
        res= self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


    def test_chat_message_history(self):

        self.client.force_authenticate(user=self.member)
        url = reverse('v1:chat_messages', kwargs={'group_id': self.chat_group.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['text'], "Hello testing!")

        self.client.force_authenticate(user=self.hacker)
        response2 = self.client.get(url)
        self.assertEqual(len(response2.data['results']), 0)
        
        
    def test_chat_message_history_anoun(self):
        url = reverse('v1:chat_messages', kwargs={'group_id': self.chat_group.id})
        response = self.client.get(url)     
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
         
    

    def test_update_chat_room_only_owner(self):
        url = reverse('v1:update-chatroom', kwargs={'id': self.chat_group.id})
        data = {"group_name": "New Name"}

  
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        self.client.force_authenticate(user=self.owner)
        response2 = self.client.patch(url, data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['group_name'], "New Name")

    def test_send_message_api(self):
        url = reverse('v1:send_message', kwargs={'group_id': self.chat_group.id})
        data = {"text": "Sent via API"}


        self.client.force_authenticate(user=self.hacker)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        self.client.force_authenticate(user=self.member)
        response2 = self.client.post(url, data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)
        
        
    def test_send_message_api_anoun(self):
        url = reverse('v1:send_message', kwargs={'group_id': self.chat_group.id})
        data = {"text": "Sent via API"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)