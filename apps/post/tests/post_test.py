from rest_framework.test import APITestCase
from  rest_framework import status
from django.contrib.auth import get_user_model
User=get_user_model()   
from django.urls import reverse
from ..models import Project
from rest_framework_simplejwt.tokens import RefreshToken

class PostTestcase(APITestCase):
    
    def setUp(self):
        
        user=self.user=User.objects.create_user(
            email="joonedo@gmail.com",
            password="AmanKumar!1"
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        
        
        
    def test_created_post(self):
        url= reverse("v1:post_urls-list")
        data={
            "project_name":"narrow",
            "title":"we chnage the wvfv,nfjkvnsdkorld",
            "description":"hy i sdfndkcascjksn cjkvnsjkvdncsdv"
        }
        res=self.client.post(url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        
    def test_empty_data(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{},format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST) 
        
    def test_missing_project_name(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"title":"we chnage the wirkd","description":"vfvfnvkvvdvdsvvfvcdcxzczv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_missing_project_title(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"project_name":"connect","description":"vfvfnvkvvdvdsvvfvcdcxzczv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    def test_missing_project_description(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"title":"we chnage the wirkd","project_name":"vfvfnv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_unauthenticated_user_create_post(self):
        self.client.credentials()
        url= reverse("v1:post_urls-list")
        data={
              "project_name":"narrow",
              "title":"we chnage the wvfv,nfjkvnsdkorld",
            "description":"hy i sdfndkcascjksn cjkvnsjkvdncsdv"
        }
        res=self.client.post(url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
            
            
            
        
            
            
            
    
        
        
        
        
            
        
        
        
        
        
        
        