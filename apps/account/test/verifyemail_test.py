from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
    
from  apps.account.models import Emailverifiction

user=get_user_model()


class VerifyEmailTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = user.objects.create_user(email="test@example.com", password="Pass1234!")
        self.token = "dummy_token"
        Emailverifiction.objects.create(
            user=self.user,
            token_hash=self.token,
            purpose="VERIFY",
            used_it=False,
        )

    def test_verify_email_success(self):
        url = reverse("v1:email-verify", args=[self.token])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
    def test_verify_email_expired_token(self):
        expired_token = Emailverifiction.objects.create(
            user=self.user,
            token_hash="expire_token",
            purpose="VERIFY",
            used_it=False,
        )
        expired_token.created_at = timezone.now() - timezone.timedelta(hours=2)
        expired_token.save()

        url = reverse("v1:email-verify", args=[expired_token.token_hash])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

        
    def test_verify_email_used_token(self):
        
        Emailverifiction.objects.filter(token_hash=self.token).update(used_it=True)
        url = reverse("v1:email-verify", args=[self.token])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

        
        
    def test_verify_email_invalid_token(self):
        url = reverse("v1:email-verify", args=["invalid_token"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        
