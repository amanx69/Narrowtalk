from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import *
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken




class SaveProjectTests(APITestCase):
    
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
        self.url=reverse('v1:project-save',args=[self.project.id])
        
        
    def test_save_project(self):
        
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data['project_id'],self.project.id)
            
        
    def test_save_project_anon_user(self):
        self.client.credentials()
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
     
    def test_current_user_save_list(self):
        urls=reverse("v1:save-project-list")
        res=self.client.get(urls)
        self.assertEqual(res.status_code,status.HTTP_200_OK)    
     
    def test_current_user_save_list_anon_user(self):
        self.client.credentials()
        urls=reverse("v1:save-project-list")
        res=self.client.get(urls)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)