from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import *
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User=get_user_model()
class UserApplictionTests(APITestCase):
    
    def setUp(self):
        
        self.user=User.objects.create_user(
            email="testemail@gmail.com",
            password='Ashu2252004'
        )
        self.project=Project.objects.create(
            title="i make blog bakcned",
            description="hyy brother",
            project_name="narrowthink",
            owner=self.user
        )
        
        self.role= RoleNeeded.objects.create(
            application_count=1,
            project=self.project,
            title='we hire the smart and caldited',
            description="hyyy brother",
            
        )
        self.applied_user=User.objects.create_user(
            email="applieduser@gmail.com",
            password='Applieduser'
        )
        self.Appliction=Application.objects.create(
                user=self.applied_user,
                role=self.role,
                message='we change the world',
                apply_role_purpose='backend'
            
        )
        self.member=Membership.objects.create(
            project=self.project,
            is_active=True,
            user=self.applied_user,
            
        )
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        
        token=RefreshToken.for_user(self.applied_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        
    def login_another_user(self,user):
        
        token=RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
            
                
        
      
    
    def test_applied_user_application_list(self):
        url=reverse('v1:applied_userappliction_list')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Application.objects.count(),1)
        
    def test_applied_user_application_list_anou_user(self):
        self.client.credentials()
        url=reverse('v1:applied_userappliction_list')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_applied_user_application_detiles(self):
        
        url=reverse('v1:applied_userappliction_detail',args=[self.Appliction.id])
        res= self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data['apply_role_purpose'],'backend')
        
    def test_applied_user_application_detilas_other_user(self):
        url=reverse('v1:applied_userappliction_detail',args=[self.Appliction.id])
        self.Appliction.user=self.user
        self.Appliction.save(update_fields=['user'])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
            
        
        
    
    def test_applied_user_application_detiles_anou_user(self):
        self.client.credentials()
        url=reverse('v1:applied_userappliction_detail',args=[self.Appliction.id])
        res= self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
        
    def test_applied_user_accpected_appliction(self):
        
        url=reverse('v1:applied_user_accpeted_appliction')
        
        self.Appliction.status='accepted'
        self.Appliction.save(update_fields=['status'])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data[0]['message'],"we change the world")
        
        
    
    def test_applied_user_accpected_appliction_anon_user(self):
        self.client.credentials()
        url=reverse('v1:applied_user_accpeted_appliction')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_join_project_detiles(self):
        
        url=reverse('v1:join_project_list')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
      
    def test_join_project_detiles_anou_user(self):
        self.client.credentials()
        url=reverse('v1:join_project_list')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_leave_project(self):
     
        url=reverse('v1:leave_project',args=[self.project.id])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_leave_project_not_member(self):
     
        url=reverse('v1:leave_project',args=[self.project.id])
        self.member.user=self.user
        self.member.save(update_fields=['user'])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        
        
    def test_leave_project_not_member_anou_user(self):
        self.client.credentials()
        url=reverse('v1:leave_project',args=[self.project.id])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_leave_project_already_leave(self):
        url=reverse('v1:leave_project',args=[self.project.id])
        self.member.is_active=False
        self.member.save(update_fields=['is_active'])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
