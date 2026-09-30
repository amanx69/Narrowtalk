from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from apps.post.models import Project
from .models import Report
User= get_user_model()


class BlockUserTestcase(APITestCase):
    def setUp(self):
        self.blocker= User.objects.create_user(
            email="ashu@gmail.com",
            password="Amankumarashu"
        )
        
        self.blocked_user=User.objects.create_user(
            email="Aman@gmail.com",
            password="Ashu2252004"
        )
        
        self.urls=reverse("v1:block_user",args=[self.blocked_user.id])
        
    def  test_block_user(self):
        self.client.force_authenticate(user=self.blocker)
        res=self.client.post(self.urls)
        unblock_res=self.client.post(self.urls)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        self.assertEqual(unblock_res.status_code,status.HTTP_200_OK)
    
    def  test_block_user_anoun(self):
   
        res=self.client.post(self.urls)
        unblock_res=self.client.post(self.urls)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unblock_res.status_code,status.HTTP_401_UNAUTHORIZED)
        

# report test 


class ReportCreateTestcase(APITestCase):
    
    def setUp(self):
        self.reporter = User.objects.create_user(
            email="reporter@gmail.com",
            password="testpassword123"
        )
        
        self.bad_user = User.objects.create_user(
            email="badguy@gmail.com",
            password="testpassword123"
        )
        
        self.bad_project = Project.objects.create(
            owner=self.bad_user,
            title="Spam Project",
            project_name="Spammer",
            description="This is a fake project for spam."
        )
        
        self.url= reverse('v1:create_report')
        
        
    def test_create_report(self):
        self.client.force_authenticate(user=self.reporter)
        data={
            "reason": Report.ReportReason.FAKE_PROFILE,
            "description": "This account is impersonating someone else.",
            "reported_user": str(self.bad_user.id)
            
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        
    def test_create_report_anoun(self):
  
        data={
            "reason": Report.ReportReason.FAKE_PROFILE,
            "description": "This account is impersonating someone else.",
            "reported_user": str(self.bad_user.id)
                
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

            
    def test_report_user_success(self):
        self.client.force_authenticate(user=self.reporter)
        data = {
            "reason": Report.ReportReason.FAKE_PROFILE,
            "description": "This account is impersonating someone else.",
            "reported_user": str(self.bad_user.id)
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(Report.objects.first().reported_user, self.bad_user)
        
             
    def test_report_user_success_anoun(self):
        data = {
            "reason": Report.ReportReason.FAKE_PROFILE,
            "description": "This account is impersonating someone else.",
            "reported_user": str(self.bad_user.id)
            }
            
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_report_project_success(self):
  
        self.client.force_authenticate(user=self.reporter)
        data = {
            "reason": Report.ReportReason.SPAM,
            "description": "Fake project asking for money.",
            "reported_project": str(self.bad_project.id)
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(Report.objects.first().reported_project, self.bad_project)
        
        
    def test_report_project_success_anoun(self):
  

        data = {
            "reason": Report.ReportReason.SPAM,
            "description": "Fake project asking for money.",
            "reported_project": str(self.bad_project.id)
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
       
    def test_report_both_fails(self):

        self.client.force_authenticate(user=self.reporter)
        data = {
            "reason": Report.ReportReason.SPAM,
            "reported_user": str(self.bad_user.id),
            "reported_project": str(self.bad_project.id)
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)