from ..models import  Project,RoleNeeded ,RequestJoinProjet
from rest_framework import serializers
from apps.Profile.models import Skill
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
User= get_user_model()



class TestSendRequestAccpectedFeathures(APITestCase):
    def setUp(self):
     
        self.request_sender=User.objects.create_user(
            email="joonedo@gmail.com",
            password="AmanKumar!1"
             )
        self.request_receiver=User.objects.create_user(
                    email="milkel@gmail.com",
                    password="AmanKumar!1"
                     )
        self.other_user=User.objects.create_user(
            email="otheruser@gmail.com",
            password="AmanKumar!1"
        )
                             
        
        self.project=Project.objects.create(
            project_name="connect",
            title="we chnage the wirkd",
            description="vfvfnvkvvdvdsvvfvcdcxzczv",
            owner=self.request_sender
                    
                )
        self.other_project=Project.objects.create(
                project_name="connect",
                title="we chnage the wirkd",
                description="vfvfnvkvvdvdsvvfvcdcxzczv",
                owner=self.other_user
                            
                        )
          
        self.role= RoleNeeded.objects.create(
            title="i wnat to best dev",
            description="hyy brothr can you make to this project",
            project=self.project,
                    
                    
            )
        self.other_role= RoleNeeded.objects.create(
            title="i wnat to best dev",
            description="hyy brothr can you make to this project",
            project=self.other_project,
                            
                            
            )
                
        self.url=reverse('v1:send_request')
        
    def test_create_request(self):
        self.client.force_authenticate(user=self.request_sender)
        data={
            "receiver_user":self.request_receiver.id,
            "project":self.project.id,
            "role":self.role.id,
            "message":"i need you"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        
    def test_create_request_for_anon_project(self):
        self.client.force_authenticate(user=self.request_sender)
        data={
            "receiver_user":self.request_receiver.id,
            "project":self.other_project.id,
            "role":self.role.id,
            "message":"i need you"
        }
        res= self.client.post(self.url,data)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
           
    def test_create_request_for_anoun_project_role(self):
        self.client.force_authenticate(user=self.request_sender)
        data={
            "receiver_user":self.request_receiver.id,
            "project":self.project.id,
            "role":self.other_role.id,
            "message":"i need you"
            }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
         
    def test_create_request_anoun(self):
        data={
            "receiver_user":self.request_receiver.id,
            "project":self.project.id,
            "role":self.role.id,
            "message":"i need you"
        }
        res= self.client.post(self.url,data)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
    
    def test_create_duplicate_request(self):
        self.client.force_authenticate(user=self.request_sender)
        data={
            "receiver_user":self.request_receiver.id,
            "project":self.project.id,
            "role":self.role.id,
            "message":"i need you"
            }
        FirestRes=self.client.post(self.url,data)
        SecRes=self.client.post(self.url,data)
        self.assertEqual(SecRes.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_accpect_request(self):
        
        self.client.force_authenticate(user=self.other_user)
        Req_Appliction= RequestJoinProjet.objects.create(
            
            receiver_user=self.other_user,
            request_owner=self.request_sender,
            project=self.project,
            role=self.role,
            message="we change the world"
        )
        url=reverse('v1:accpect_join_request',args=[Req_Appliction.id])
        res=self.client.patch(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
        
    def test_permission_accpect_request_views(self):
            
        self.client.force_authenticate(user=self.request_receiver)
        Req_Appliction= RequestJoinProjet.objects.create(
                
            receiver_user=self.other_user,
            request_owner=self.request_sender,
            project=self.project,
            role=self.role,
            message="we change the world"
        )
        url=reverse('v1:accpect_join_request',args=[Req_Appliction.id])
        res=self.client.patch(url)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
            
            
            
    def test_reject_request(self):
        self.client.force_authenticate(user=self.other_user)
        req_application = RequestJoinProjet.objects.create(
            receiver_user=self.other_user,
            request_owner=self.request_sender,
            project=self.project,
            role=self.role,
            message="we change the world"
        )
        url = reverse('v1:reject_join_request', args=[req_application.id]) 
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_send_request_to_active_member(self):
        from apps.post.models import Membership
        Membership.objects.create(
            user=self.request_receiver, 
            project=self.project, 
            role_title=self.role.role, 
            is_active=True
        )
        self.client.force_authenticate(user=self.request_sender)
        data = {
            "receiver_user": self.request_receiver.id,
            "project": self.project.id,
            "role": self.role.id,
            "message": "i need you"
        }
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_accept_request_already_member(self):
        self.client.force_authenticate(user=self.other_user)
   
        from apps.post.models import Membership
        Membership.objects.create(
            user=self.other_user, 
            project=self.project, 
            role_title=self.role.role, 
            is_active=True
        )
        
        req_application = RequestJoinProjet.objects.create(
            receiver_user=self.other_user,
            request_owner=self.request_sender,
            project=self.project,
            role=self.role,
            message="we change the world"
        )
        url = reverse('v1:accpect_join_request', args=[req_application.id])
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        
        
# test current user prject list
    def test_current_user_project(self):
        self.client.force_authenticate(user=self.request_sender)
        url=reverse('v1:current_user_project_names')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_list_of_pending_request(self):
        self.client.force_authenticate(user=self.request_receiver)
        url=reverse('v1:pending_requests_list')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
    def test_list_of_pending_request_anon_user(self):
        url=reverse('v1:pending_requests_list')
        res=self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
    def test_pending_request_detiles(self):
        self.client.force_authenticate(user=self.request_receiver)
        req= RequestJoinProjet.objects.create(
         request_owner=self.request_sender,
         receiver_user=self.request_receiver,
         message="hyy we are change",
         project=self.project,
         role=self.role
            
        )
        url= reverse("v1:pending_request_detail",args=[req.id])
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        
    def test_pending_request_detiles(self):
      
        req= RequestJoinProjet.objects.create(
         request_owner=self.request_sender,
         receiver_user=self.request_receiver,
         message="hyy we are change",
         project=self.project,
         role=self.role
            
        )
        url= reverse("v1:pending_request_detail",args=[req.id])
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        

    def test_list_of_sent_request(self):
        self.client.force_authenticate(user=self.request_sender)
        RequestJoinProjet.objects.create(
            request_owner=self.request_sender,
            receiver_user=self.request_receiver,
            message="hyy I want you to join",
            project=self.project,
            role=self.role
        )
        url = reverse('v1:sent_requests_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_list_of_sent_request_anon(self):
        url = reverse('v1:sent_requests_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)