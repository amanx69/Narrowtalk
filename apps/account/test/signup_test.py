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
        self.url = reverse('v1:Signup')  
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
        