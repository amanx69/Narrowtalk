from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
import hashlib
from  apps.account.models import Emailverifiction

user=get_user_model()


class VerifyEmailTestCase(TestCase):
    
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = user.objects.create_user(email="test@example.com", password="Pass1234!")
        self.otp="458745"
        hash_otp=hashlib.sha256(self.otp.encode()).hexdigest()
        self.verify=Emailverifiction.objects.create(
            user=self.user,
           otp=hash_otp,
            used_it=False,
        )
        self.url= reverse("v1:email-verify")

    def test_verify_email_success(self):
        
        data={
            "email":f"{self.user.email}",
            "otp":f'{self.otp}'
        }
        response = self.client.post(self.url,data)
        self.assertEqual(response.status_code, 200)
       

    def test_verify_email_expired_otp(self):
        self.verify.created_at = timezone.now() - timezone.timedelta(hours=2)
        self.verify.save()
        data={
                "email":f"{self.user.email}",
                "otp":f'{self.otp}'
            }

        response = self.client.post(self.url,data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"],"This OTP has expired. Please request a new one.")

    
    def test_attempts_for_verify_email(self):
        self.verify.attempts=3
        self.verify.save(update_fields=['attempts'])
        data={
             
                "email":f"{self.user.email}",
                "otp":f"{self.otp}"
            
        }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"Too many invalid attempts. Please request a new OTP.")
        
    def test_worng_otp(self):
        data={
          
            "email":f"{self.user.email}",
            "otp":f"544475"
                    
                }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"Invalid OTP entered. Please try again.")
        
        

    def test_without_email(self):
        data={
         
            "email":f"",
            "otp":f"{self.otp}"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_without_otp(self):
        data={
       
            "email":f"{self.user.email}",
            "otp":f""
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_not_regester_email(self):
        data={
            
                "email":f"Notregenter@gmaail.com",
                "otp":f"457844"
            }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"This OTP has expired. Please request a new one.")


    def test_short_otp(self):
        data={
       
            "email":f"{self.user.email}",
            "otp":f"44"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    
            
        