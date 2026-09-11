from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import *
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken



User=get_user_model()

class LIkeTest(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user(
            email="ashu@gmail.com",
            password="Ashukumar"
        )
        
        self.project= Project.objects.create(
            owner=self.user,
            title="we are good",
            description="anshu kumari my love ",
            project_name='connecteach',
            
        )
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        self.url=reverse('v1:project-like',args=[self.project.id])
        
    def test_like_project(self):
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data['project_id'],self.project.id)
                
                
    def test_like_project_anou_user(self):
        self.client.credentials()
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_ratelimite(self):
        
        for _ in range(30):
            res=self.client.post(self.url)
            self.assertEqual(res.status_code,status.HTTP_200_OK)
            
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)