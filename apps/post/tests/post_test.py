from rest_framework.test import APITestCase
from  rest_framework import status
from django.contrib.auth import get_user_model
User=get_user_model()   
from django.urls import reverse
from ..models import Project
from rest_framework_simplejwt.tokens import RefreshToken

class PostTestcase(APITestCase):
    
    def setUp(self):
        
        self.user=self.user=User.objects.create_user(
            email="joonedo@gmail.com",
            password="AmanKumar!1"
        )
        self.project=Project.objects.create(
            project_name="connect",
            title="we chnage the wirkd",
            description="vfvfnvkvvdvdsvvfvcdcxzczv",
            owner=self.user
            
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
    def other_user(self):
        other_user=User.objects.create_user(
                    email="dumfdcmy@gmail.com",
                    password="Amankumar1!",
            )
        return other_user
                    
            

        
        
        
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
    def test_short_project_name(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"project_name":"c","title":"we chnage the wirkd","description":"vfvfnvkvvdvdsvvfvcdcxzczv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_long_project_name(self):
        url=reverse('v1:post_urls-list')
        res=self.client.post(url,{"project_name":"c"*51,"title":"we chnage the wirkd","description":"vfvfnvkvvdvdsvvfvcdcxzczv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_short_project_title(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"project_name":"connect","title":"w","description":"vfvfnvkvvdvdsvvfvcdcxzczv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_long_project_title(self):
        url= reverse('v1:post_urls-list')
        res=self.client.post(url,{"project_name":"connect","title":"w"*151,"description":"vfvfnvkvvdvdsvvfvcdcxzczv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_short_project_description(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"project_name":"connect","title":"we chnage the wirkd","description":"vfv"})
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    def test_long_project_description(self):
        url= reverse("v1:post_urls-list")
        res=self.client.post(url,{"project_name":"connect","title":"we chnage the wirkd","description":"vfv"*50})
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
        
    def test_get_post_list(self):
        url= reverse("v1:post_urls-list")
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_get_post_detail(self):
        url = reverse("v1:post_urls-detail", args=[self.project.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def other_user_get_post_detail(self):
        other_user=User.objects.create_user(
            email="dummy@gmail.com",
            password="AmanKumar!1"
        )
        refresh = RefreshToken.for_user(other_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
        url= reverse("v1:post_urls-detail", args=[self.project.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
        
        
    def test_update_post(self):
        url = reverse("v1:post_urls-detail", args=[self.project.id])
        data = {
            "project_name": "updatcded_project",
            "title": "Updated Title",
            "description": "Updated Description"
        }
        res = self.client.patch(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.project_name, data["project_name"])
        self.assertEqual(self.project.title, data["title"])
        self.assertEqual(self.project.description, data["description"])
        
    def test_update_post_by_non_owner(self):
        other_user=User.objects.create_user(
            email="dummy@gmail.com",
            password="AmanKumar!1"
        )
        refresh = RefreshToken.for_user(other_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url= reverse("v1:post_urls-detail", args=[self.project.id])
        res=self.client.patch(url,{"title":"updated title"})
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
        
    def test_delete_post(self):
        project = Project.objects.create(
            project_name="delete_project",
            title="Delete Title",
            description="Description for delete project",
            owner=self.user,
            is_delete=False,
            is_active=True,
        )
        
        url = reverse("v1:post_urls-detail", args=[project.id])
        res = self.client.delete(url)
        project.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(project.is_delete, True)
        self.assertEqual(project.is_active, False)
        
    def test_delete_post_by_non_owner(self):
        other_user=User.objects.create_user(
                    email="dummy@gmail.com",
                    password="AmanKumar!1"
                )
        refresh = RefreshToken.for_user(other_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
        url = reverse("v1:post_urls-detail", args=[self.project.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_post_by_unauthenticated_user(self):
        self.client.credentials()  
        url = reverse("v1:post_urls-detail", args=[self.project.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
    def close_post(self):
        url = reverse("v1:post_urls-close-project", args=[self.project.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.is_active, False)
        
    def test_close_post_by_non_owner(self):
        other_user=User.objects.create_user(
                    email="dummy@gmail.com",
                    password="Amankumar1!",
        )
        refresh = RefreshToken.for_user(other_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
        url = reverse("v1:post_urls-close-project", args=[self.project.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def get_project_memebers(self):
        url=reverse("v1:post_urls-get-project-member", args=[self.project.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
'''remove this test beacause it is not needed as we are not
allowing non-owner to get project members my feathure all used see who join the project and what role they have''' 
#   def test_get_project_memebers_by_non_owner(self):
#         other_user=User.objects.create_user(
#                             email="dummy@gmail.com",
#                             password="Amankumar1!",
#                 )
#         refresh = RefreshToken.for_user(other_user)
#         self.access_token = str(refresh.access_token)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
      
#         url=reverse("v1:post_urls-get-project-member", args=[self.project.id])
#         res=self.client.get(url)
#         self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
        
         
        
    
        
            
            
        
            
            
            
    
        
        
        
        
            
        
        
        
        
        
        
        