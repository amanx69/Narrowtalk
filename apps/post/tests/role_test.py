from ..models import  Project,RoleNeeded
from rest_framework import serializers
from apps.Profile.models import Skill
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
User= get_user_model()



class TestRoleClass(APITestCase):
    
    def setUp(self):
        cache.clear()
        
        self.user=User.objects.create_user(
            email="aman@gmail.com",
            password="Amankumar1!",
        )
        self.project=Project.objects.create(
            owner=self.user,
            title="Test Project",
            project_name="test_project",
            description="This is a test project.",
            
        )
        
        self.role= RoleNeeded.objects.create(
                title="i wnat to best dev",
                description="hyy brothr can you make to this project",
                project=self.project,
            
            
            )
        
        
        self.url=reverse('v1:post_urls-roles', args=[self.project.id])
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
      
    
    def test_created_role(self):
        url=reverse('v1:post_urls-roles', args=[self.project.id])
        data={
                "title":"Test Role",
                "description":"This is a test role.",
                "slots_available":2,
                "required_skills": [
                 {"name": "Django"},
                 {"name": "Python"},
        ],
              
            }
        res=self.client.post(url,data, format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        
    def test_create_role_unauthorized_user(self):
        self.client.credentials()
        data={
            "title":"Test Role",
            "description":"This is a test role.",
            "slots_available":2,
                           }
        res=self.client.post(self.url, data )
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
               
                   
    def test_get_roles(self):
        url=reverse('v1:post_urls-roles', args=[self.project.id])
        res=self.client.get(url)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_missing_title(self):
        res=self.client.post(self.url,{"title":"","description":"vmdnbchdcdcdhcbjdc"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_without_skill(self):
        
        data={
            "title":"Test Role",
            "description":"This is a test role.",
            "slots_available":2
                          
            }
        res=self.client.post(self.url,data,format="json")
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_missing_dec(self):
        res=self.client.post(self.url,{"title":"anshu kuamri my life line my love ❤️","description":""})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_delete_role(self):
        role= RoleNeeded.objects.create(
            title="i wnat to best dev",
            description="hyy brothr can you make to this project",
            project=self.project
        )
        url=reverse('v1:post_urls-delete_role',args=[self.project.id,role.id])
        res=self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        
    def test_other_user_deleted(self):
        other_user= User.objects.create_user(
            email="anujaman@gmmail.com",
            password="amankumar1@"
        )
        token=RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        url=reverse('v1:post_urls-delete_role',args=[self.project.id,self.role.id])
        res=self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
                
   
     
    def test_role_detiels(self):
        url=reverse('v1:post_urls-edit_and_get_role',args=[self.project.id,self.role.id])
        res=self.client.get(url,format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_role_detiels_anou_user(self):
        self.client.credentials()
        url=reverse('v1:post_urls-edit_and_get_role',args=[self.project.id,self.role.id])
        res=self.client.get(url,format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_update_role(self):
        url=reverse('v1:post_urls-edit_and_get_role',args=[self.project.id,self.role.id])
        data={
            "title":"aman kumar test"
        }
        res=self.client.patch(url,data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_update_role_anou_user(self):
        self.client.credentials()
        url=reverse('v1:post_urls-edit_and_get_role',args=[self.project.id,self.role.id])
        data={
            "title":"aman kumar test"
        }
        res=self.client.patch(url,data)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_update_other_user(self):
        other_user=User.objects.create_user(
            email="other@gmail.com",
            password="Amankumar@144"
        )
        token=RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        url=reverse('v1:post_urls-edit_and_get_role',args=[self.project.id,self.role.id])
        data={
            "title":"update title"
        }
        res=self.client.patch(url,data)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
          
        
      
        
        
        
        

                                            


 