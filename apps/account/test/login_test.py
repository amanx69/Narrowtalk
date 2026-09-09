from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
    
from  apps.account.models import Emailverifiction

user=get_user_model()





class Logintest(APITestCase):
        
    def setUp(self):
        cache.clear()
        self.url = reverse('v1:Login')
        self.password = "Test@1234"
        self.email = "test@gmail.com"
        self.valid_data = {
            "email": self.email,
            "password": self.password,
        }
        self.user = user.objects.create_user(
            email=self.email, password=self.password, is_verify=True
        )
        
        ##! test rate limit

    # def test_rate_limit(self):
    #     for _ in range(5):
        
    #         res= self.client.post(self.url, self.valid_data)
    #         self.assertIn(res.status_code, [status.HTTP_200_OK])
    #     response = self.client.post(self.url, self.valid_data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        
        
    def test_login_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login successful")
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_login_wrong_password(self):
        data = self.valid_data.copy()
        data["password"] = "Wrong@1234"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_email(self):
        data = self.valid_data.copy()
        data["email"] = "unknown@gmail.com"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_email_not_verified(self):
        unverified_user = user.objects.create_user(
            email="unverified@gmail.com", password=self.password, is_verify=False
        )
        data = {
            "email": unverified_user.email,
            "password": self.password,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_account(self):
        inactive_user = user.objects.create_user(
            email="inactive@gmail.com", password=self.password, is_verify=True, is_active=False
        )
        data = {
            "email": inactive_user.email,
            "password": self.password,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_email_format(self):
        data = self.valid_data.copy()
        data["email"] = "not-an-email"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_data(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        

    

