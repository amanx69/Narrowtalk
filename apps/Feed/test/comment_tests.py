from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import *
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken



User=get_user_model()



class CommentTests(APITestCase):
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
            comment_count=1
            
        )
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        self.url=reverse('v1:project-comment',args=[self.project.id])
        
        
    

    def test_create_comment(self):
        
        data={
            "text":"We change the world"
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        Commnet_count=self.project.comment_count
        self.assertEqual(Commnet_count,1)
        
        
    def test_short_comment(self):
        
        data={
             "text":"W"
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
            
    def test_empty_comment(self):
        
        data={
             "text":""
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
         
    def test_without_comment(self):
         res=self.client.post(self.url,{},format='json')
         self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
         
         
    def test_get_current_project_comment(self):
        res=self.client.get(self.url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_get_current_project_comment_anou_user(self):
        self.client.credentials()
        res=self.client.get(self.url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
             
   
    def test_delete_comment(self):
        comment=Projectcomment.objects.create(
            text=" for delete the comment",
            project=self.project,
            user=self.user
        )
        urls=reverse('v1:deleted_comment',args=[self.project.id,comment.id])
        res=self.client.delete(urls)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        
    def test_delete_comment_anou_user(self):
        self.client.credentials()
        comment=Projectcomment.objects.create(
            text=" for delete the comment",
            project=self.project,
            user=self.user
        )
        urls=reverse('v1:deleted_comment',args=[self.project.id,comment.id])
        res=self.client.delete(urls)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_by_other_user(self):
        
        other_user=User.objects.create_user(
            email="Otheruser@gmail.com",
            password="Ashukumar"
        )
        token=RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        
        comment=Projectcomment.objects.create(
            text=" for delete thehr comment",
            project=self.project,
            user=self.user
            )
        urls=reverse('v1:deleted_comment',args=[self.project.id,comment.id])
        res=self.client.delete(urls)
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        

        
        
    

        
       