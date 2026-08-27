from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.rooms.models import Room, RoomInviteLink

User = get_user_model()


class RoomInviteLinkTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email='owner@example.com', password='StrongPass123!')
        self.member = User.objects.create_user(email='member@example.com', password='StrongPass123!')
        self.room = Room.objects.create(owner=self.owner, room_name='Test Room')

    def test_valid_invite_link_allows_member_to_join(self):
        invite = RoomInviteLink.objects.create(room=self.room, user=self.owner)

        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse('join_with_token', args=[str(invite.token)]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.member, self.room.participants.all())

    def test_inactive_invite_link_is_rejected(self):
        invite = RoomInviteLink.objects.create(room=self.room, user=self.owner, is_active=False)

        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse('join_with_token', args=[str(invite.token)]))

        self.assertEqual(response.status_code, 400)
        self.assertNotIn(self.member, self.room.participants.all())
