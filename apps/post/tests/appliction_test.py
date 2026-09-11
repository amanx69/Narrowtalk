from rest_framework.test import APITestCase
from ..models import Application ,Project,RoleNeeded
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
User=get_user_model()
from django.urls import reverse



class TestAppliction(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user(
            email="test@gmail.com",
            password="Amankumar@4"
        )
        self.project=Project.objects.create(
            project_name="connect_each",
            title="we chnage the wirkd",
            description="vfvfnvkvvdvdsvvfvcdcxzczv",
            owner=self.user
        )
        self.role=RoleNeeded.objects.create(
            project=self.project,
            title="i need dev",
            description='we change the world',
            application_count=1,
        )
        self.other_user=User.objects.create_user(
            email="otherucser@gmail.com",
            password="Amankumar124"
            )
       
        self.url=reverse('v1:appliction',args=[self.role.id])
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        
    def login_other_user(self,user):
        token=RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        
                
            
        
    
    def test_apply_appliction(self):
        data={
            "apply_role_purpose":'backend',
            "message":"hyy bro i want to join"
        }
        res=self.client.post(self.url,data,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        
    def test_apply_unauthorized_user(self):
        self.client.credentials()
        data={
                "apply_role_purpose":'backend',
                "message":"hyy bro i want to join"
            }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_blank_message(self):
        data={
            "message":"",
            "apply_role_purpose":'backend',
                }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_short_message(self):
        
        data={
            "message":"ashu",
            "apply_role_purpose":'backend',
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_long_message(self):
        data={
            "message":"A"*50000,
            "apply_role_purpose":'backend',
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_without_apply_role(self):
        data={
        "message":"ashu kumari",
        "apply_role_purpose":"",
                }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_withdraw_appliction(self):
        token=RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        self.appliction=Application.objects.create(
            user=self.user,
            role=self.role,
            message='we change the world',
            apply_role_purpose='backend'
                                    
        )         
        url=reverse('v1:withdraw_app',args=[self.appliction.id])
        res=self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
        #! all test for owenr_appliction_user
    def test_accpect_appliction(self):
        appliction=Application.objects.create(
            user=self.user,
            role=self.role,
            message='we change the world',
            apply_role_purpose='backend'
                                            
                )         
        url=reverse('v1:accpect_app',args=[appliction.id])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_accpect_appliction_anou_user(self):
        self.client.credentials()
        appliction=Application.objects.create(
            user=self.user,
            role=self.role,
            message='we change the world',
            apply_role_purpose='backend'
                                            
                )         
        url=reverse('v1:accpect_app',args=[appliction.id])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
        
      
    def test_rejected_appliction(self):
        appliction=Application.objects.create(
            user=self.user,
            role=self.role,
            message='we change the world',
            apply_role_purpose='backend'
                                            
                )         
        url=reverse('v1:rejected_app',args=[appliction.id])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_rejected_appliction_anou_user(self):
        self.client.credentials()
        appliction=Application.objects.create(
            user=self.user,
            role=self.role,
            message='we change the world',
            apply_role_purpose='backend'
                                            
                )         
        url=reverse('v1:rejected_app',args=[appliction.id])
        res=self.client.post(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
        
     
    def test_single_appliction_detiles(self):
        appliction=Application.objects.create(
            user=self.user,
            role=self.role,
            message='we change the world',
            apply_role_purpose='backend'
                                                    
            ) 
        
        url= reverse('v1:getsingle-appliction',args=[appliction.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
          
        
    def test_single_appliction_detiles_other_user(self):
        
        other_user= User.objects.create_user(
            email="otheruser@gmail.com",
            password="otherpassword",
        )
        token=RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        appliction=Application.objects.create(
                user=self.user,
                role=self.role,
                message='we change the world',
                apply_role_purpose='backend'
                                                        
                ) 
            
        url= reverse('v1:getsingle-appliction',args=[appliction.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
        
    def test_single_appliction_anou_user(self):
        self.client.credentials()
        appliction=Application.objects.create(
                user=self.user,
                role=self.role,
                message='we change the world',
                apply_role_purpose='backend'
                                                            
                    ) 
                
        url= reverse('v1:getsingle-appliction',args=[appliction.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_get_List_pending_appliction(self):
        
        url=reverse('v1:pending_appliction',args=[self.role.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    
    def test_get_List_pending_appliction(self):
            
        url=reverse('v1:accpect_appliction',args=[self.role.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
            
    def test_get_List_pending_appliction_anou_user(self):
        self.client.credentials()
        url=reverse('v1:pending_appliction',args=[self.role.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    
    def test_get_List_pending_appliction_anou_user(self):
        self.client.credentials()    
        url=reverse('v1:accpect_appliction',args=[self.role.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
            
        
            
              
        
     
    
        

                
        
