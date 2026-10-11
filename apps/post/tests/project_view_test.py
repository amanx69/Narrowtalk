from rest_framework.test import APITestCase
from  rest_framework import status
from django.contrib.auth import get_user_model
User=get_user_model()   
from django.urls import reverse
from ..models import Project ,Membership ,RoleNeeded




class PostTestcase(APITestCase):
    
    def setUp(self):
        
        self.user=User.objects.create_user(
            email="joonedo@gmail.com",
            password="AmanKumar!1"
        )
        self.new_owner= User.objects.create_user(
            email="newowner@gmail.com",
            password="Ashukumari342"
        )
        self.project=Project.objects.create(
            project_name="connect",
            title="we chnage the wirkd",
            description="vfvfnvkvvdvdsvvfvcdcxzczv",
            owner=self.user
            
        )
        self.member= Membership.objects.create(
            project=self.project,
            user=self.new_owner,
            role_title="Backend",
            is_active=True
        )
        
    def test_transfer_owner(self):
        self.user.user_profile.project_count = 1
        self.user.user_profile.save()

        self.client.force_authenticate(user=self.user)
        url = reverse("v1:transfer_project_ownership", args=[self.project.id])
        data = {
            "new_owner_id": str(self.new_owner.id)
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.owner, self.new_owner)
        self.assertTrue(
            Membership.objects.filter(
                project=self.project, 
                user=self.user, 
                role_title="Previous Owner", 
                is_active=True
            ).exists()
        )
        self.assertFalse(
            Membership.objects.filter(project=self.project, user=self.new_owner).exists()
        )

        self.user.user_profile.refresh_from_db()
        self.assertEqual(self.user.user_profile.project_count, 0)
        self.new_owner.user_profile.refresh_from_db()
        self.assertEqual(self.new_owner.user_profile.project_count, 1)
        
        
    def test_complete_project(self):
        role = RoleNeeded.objects.create(
            project=self.project,
            title="Backend Dev",
            is_open=True,
            is_complete=False
        )

        url = reverse("v1:complete_project", args=[self.project.id])
        self.client.force_authenticate(user=self.new_owner)
        res_non_owner = self.client.post(url)
        self.assertEqual(res_non_owner.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.COMPLETED)

        # Verify role closed and completed
        role.refresh_from_db()
        self.assertFalse(role.is_open)
        self.assertTrue(role.is_complete)
        self.user.user_profile.refresh_from_db()
        self.assertEqual(self.user.user_profile.project_completed, 1)

        self.new_owner.user_profile.refresh_from_db()
        self.assertEqual(self.new_owner.user_profile.project_completed, 1)
        res_again = self.client.post(url)
        self.assertEqual(res_again.status_code, status.HTTP_400_BAD_REQUEST)