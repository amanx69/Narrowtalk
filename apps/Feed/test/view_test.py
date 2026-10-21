from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import *
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


User=get_user_model()




class ProjectViewTests(APITestCase):
    
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
        self.url=reverse('v1:project-view',args=[self.project.id])
        
        
        
    def test_view_project(self):
        
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED)
    
    def test_view_project_anou_user(self):
        self.client.credentials()
        res=self.client.post(self.url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
    