from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import *
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User=get_user_model()

class ProfileTests(APITestCase):
    
    def setUp(self):
        self.user=User.objects.create_user(
            email="amankumar@gmail.com",
            password="Ashu2252004"
        )
        self.other_user=User.objects.create_user(
            email="otheruser@gmail.com",
            password="AmanKUMAR"
        )
        
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        
        
        
        
    def test_update_profile(self):
        url=reverse('v1:user_profile')
        data={
            "username":"aman kuamr"
        }
        res=self.client.patch(url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data['username'],data['username'])
        
        
    def test_update_anou_user(self):
        self.client.credentials()
        url=reverse('v1:user_profile')
        data={
            "username":"aman kuamr"
        }
        res=self.client.patch(url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
                        
    def test_get_current_user_profile(self):
        url=reverse('v1:user_profile')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data['email'],self.user.email)

    def test_get_current_user_profile_anou_user(self):
        self.client.credentials()
        url=reverse('v1:user_profile')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
        
    def test_get_other_user_profile(self):
        url=reverse('v1:get-other-profile',args=[self.other_user.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data['email'],self.other_user.email)
        
        
    def test_get_other_user_profile_anou_user(self):
        self.client.credentials()
        url=reverse('v1:get-other-profile',args=[self.other_user.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    
    def test_profile_like(self):
        url=reverse('v1:profile-like',args=[self.other_user.user_profile.id])
        res=self.client.post(url,format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        

    def test_profile_like_anou_user(self):
        self.client.credentials()
        url=reverse('v1:profile-like',args=[self.other_user.user_profile.id])
        res=self.client.post(url,format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)