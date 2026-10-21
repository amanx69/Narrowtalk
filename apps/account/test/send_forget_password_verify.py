from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model


User= get_user_model()


class sendForgetpassWordVerifyTest(APITestCase):
    
    def setUp(self):
        self.url= reverse('v1:send-reset-email-forgetpassword')
        self.user= User.objects.create_user(
            email="test@gmail.com",
            password="Test@1234"
        )
        
        
    def test_send_forget_email(self):
        data={
            "email":"test@gmail.com"
        }
        
        res=self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, (
            status.HTTP_200_OK))
        
    def test_send_empty_email(self):
        data={
            "email":""
        }
        
        res= self.client.post(self.url ,data=data)
        self.assertEqual(res.status_code, (status.HTTP_400_BAD_REQUEST))
        
