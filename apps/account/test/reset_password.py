from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from  apps.account.models import Emailverifiction
from django.core.cache import cache
import hashlib
User=get_user_model()



class ResetPasswordTestCase(APITestCase):
    def setUp(self):   
        cache.clear()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )
        self.emali_verify=Emailverifiction.objects.create(
            user=self.user,
            otp="258745",
            
        )
        self.url= reverse('v1:reset-password')
    
    def test_reset_password(self):
        data={
            "password":"Ashu@123456",
            "email":f"{self.user.email}",
            "otp":f"{self.emali_verify.otp}"
        }
        res= self.client.post(self.url,data) 
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data["message"],"password reset successfully")
        
        
        
    def test_without_password(self):
        data={
            "password":"",
            "email":f"{self.user.email}",
            "otp":f"{self.emali_verify.otp}"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_weak_password(self):
        data={
            "password":"aman",
            "email":f"{self.user.email}",
            "otp":f"{self.emali_verify.otp}"
        }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    def test_attempts_for_reset_password(self):
        self.emali_verify.attempts=3
        self.emali_verify.save(update_fields=['attempts'])
        data={
               "password":"Ashu@123456",
                "email":f"{self.user.email}",
                "otp":f"{self.emali_verify.otp}"
            
        }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"to many attempts please resend again")
        
    def test_worng_otp(self):
        data={
            "password":"Ashu@123456",
            "email":f"{self.user.email}",
            "otp":f"544475"
                    
                }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"Please enter a correct otp")
        
        

    def test_without_email(self):
        data={
            "password":"Amnakumar@1",
            "email":f"",
            "otp":f"{self.emali_verify.otp}"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_without_otp(self):
        data={
            "password":"Amankumardahj",
            "email":f"{self.user.email}",
            "otp":f""
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_not_regester_email(self):
        data={
                "password":"Amankumarf",
                "email":f"Notregenter@gmaail.com",
                "otp":f"457844"
            }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"otp is expire please resend again")


    def test_short_otp(self):
        data={
            "password":"Anakmjjkcjkd",
            "email":f"{self.user.email}",
            "otp":f"44"
        }
        res= self.client.post(self.url,data)
        print(res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    
            
        