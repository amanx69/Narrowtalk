from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from  apps.account.models import Emailverifiction

User=get_user_model()



class ResetPasswordTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )
        self.user.is_verify = True
        self.user.save(update_fields=["is_verify"])
        self.token="dumm_token"
        self.emali_verify=Emailverifiction.objects.create(
            user=self.user,
            token_hash=self.token,
            purpose='RESETPASSWORD',
            
        )
        self.url= reverse('reset-password',kwargs={"token":self.emali_verify.token_hash})
    
    def test_reset_password(self):
        data={
            "password":"Ashu@123456"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data["message"],"password reset successfully")
        
        
        
    def test_without_password(self):
        data={
            "password":""
        }
        res= self.client.post(self.url,data)
        print(res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"password is required")
        
        
    def test_weak_password(self):
        data={
            "password":"aman"
        }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", res.data["message"].lower())
        
    def test_not_verify_user(self):
        self.user.is_verify = False
        self.user.save(update_fields=["is_verify"])

        data={
            "password":"Ashukumar!12"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["message"],"Before reset password you need to verify your email")
        