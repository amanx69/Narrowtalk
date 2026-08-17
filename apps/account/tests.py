from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
    
from  apps.account.models import Emailverifiction

user=get_user_model()



#! signup testcase
class SignUpTestCase(APITestCase):
    
    def setUp(self):
        cache.clear()
        self.url = reverse('Signup')  
        self.valid_data = {
            "email": "test@gmail.com",
            "password": "Test@1234",
          
        }   
        
    def test_rate_limit(self):
        for _ in range(5):
            
            response = self.client.post(self.url, self.valid_data)
            self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
       

            
        rspoonse= self.client.post(self.url,self.valid_data)
        self.assertEqual(rspoonse.status_code,status.HTTP_403_FORBIDDEN)
            
            
    def test_signup(self):
        
        response= self.client.post(self.url,self.valid_data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(user.objects.count(),1)
        
        
    def test_duplicate_email(self):
        self.client.post(self.url,self.valid_data)
        response= self.client.post(self.url,self.valid_data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        
        
        
    def test_wrong_password(self):
        data=self.valid_data.copy()
        data['password']="abc"
        response= self.client.post(self.url,data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_signup_invalid_email(self):
        data=self.valid_data.copy()
        data['email']="amankumar"
        response= self.client.post(self.url,data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
    
        
    def test_signup_empty_data(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        


#! login test case
class Logintest(APITestCase):
        
    def setUp(self):
        cache.clear()
        self.url = reverse('Login')
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

    def test_rate_limit(self):
        for _ in range(5):
        
            res= self.client.post(self.url, self.valid_data)
            self.assertIn(res.status_code, [status.HTTP_200_OK])
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        
        
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
        url = reverse("email-verify", args=[self.token])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
    def test_verify_email_expired_token(self):
        expired_token = Emailverifiction.objects.create(
            user=self.user,
            token_hash="expired_token",
            purpose="VERIFY",
            used_it=False,
        )
        expired_token.created_at = timezone.now() - timezone.timedelta(hours=2)
        expired_token.save()

        url = reverse("email-verify", args=[expired_token.token_hash])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("your token is expire resent again", response.data["message"])
        
    def test_verify_email_used_token(self):
        
        Emailverifiction.objects.filter(token_hash=self.token).update(used_it=True)
        url = reverse("email-verify", args=[self.token])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("your token is already used", response.data["message"])
        
        
    def test_verify_email_invalid_token(self):
        url = reverse("email-verify", args=["invalid_token"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        
