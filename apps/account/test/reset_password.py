from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from  apps.account.models import Emailverifiction , PasswordResetToken
from django.core.cache import cache
import hashlib
User=get_user_model()
import secrets
from datetime import timedelta
from django.utils import timezone

class ResetPasswordTestCase(APITestCase):
    def setUp(self):   
        cache.clear()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )
        self.otp="456258"
        self.token=secrets.token_urlsafe(36)
        hash_otp=hashlib.sha256(self.otp.encode()).hexdigest()
        hash_token=hashlib.sha256(self.token.encode()).hexdigest()
        self.emali_verify=Emailverifiction.objects.create(
            user=self.user,
            otp=hash_otp,
        )
        self.user_token=PasswordResetToken.objects.create(
            user=self.user,
            token=hash_token,
            expires_at=timezone.now() + timedelta(minutes=10),
                        
        )
        self.url= reverse('v1:reset-password')
        self.otp_url=reverse("v1:verify-otp-reset-password")
        
    def test_verify_otp(self):
        data={
            "email":f"{self.user.email}",
            "otp":f"{self.otp}"
        }
        res=self.client.post(self.otp_url,data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    
    def test_reset_password(self):
        data={
             "password":"Ashu@123456",
             "token":f"{self.token}"
         
         }
        res= self.client.post(self.url,data) 
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data["message"],"password reset successfully")
        
        
        
    def test_without_password(self):
        data={
            "password":"",
            "token":f"{self.token}"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_weak_password(self):
        data={
            "password":"aman",
            "token": self.token
       
        }
        res=self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        

        
    def test_worng_otp(self):
        data={
            "email":f"{self.user.email}",
            "otp":"458587"
                    
                }
        res=self.client.post(self.otp_url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['message'],"Invalid OTP entered. Please try again.")
        
        

    def test_without_email(self):
        data={
            "email":f"",
            "otp":f"{self.otp}"
        }
        res= self.client.post(self.otp_url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_without_otp(self):
        data={

             "email":f"{self.user.email}",
             "otp":f""
         }
        res= self.client.post(self.otp_url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_not_regester_email(self):
        data={
                
                "email":f"Notregenter@gmaail.com",
                "otp":f"457844"
            }
        res= self.client.post(self.otp_url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)



    def test_short_otp(self):
        data={
           
            "email":f"{self.user.email}",
            "otp":f"44"
        }
        res= self.client.post(self.otp_url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    
    def test_reset_password_expired_token(self):
        from django.utils import timezone
        self.user_token.expires_at = timezone.now() -timezone.timedelta(minutes=10)
        self.user_token.save()
        data={
              "password":"Amankumar145",
              "token":self.token
             }

        response = self.client.post(self.url,data)
        self.assertEqual(response.status_code, 400)

        
        
    def test_verify_otp_expire(self):
            from django.utils import timezone
            self.emali_verify.created_at = timezone.now() - timezone.timedelta(minutes=20)
            
            self.emali_verify.save(update_fields=['created_at'])
            print(self.emali_verify.created_at)
            data={
                "email":self.user.email,
                "otp":self.otp
                }

            response = self.client.post(self.otp_url,data)
            print(response.data)
            self.assertEqual(response.status_code, 400)
            
        