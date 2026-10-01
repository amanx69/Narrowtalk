from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
User=get_user_model()
from rest_framework import status


class FeedbackApiTest(APITestCase):
    def setUp(self):
        
        self.user= User.objects.create_user(
            email="aman@gmail.com",
            password="Amankumarsahu"
        )
        
        self.url=  reverse('v1:feedback')
        
        
    def test_create_feedback(self):
        self.client.force_authenticate(user=self.user)
        data={
            "title":"for this type of  bug",
            
            "description":" fix this bug ro you know this is cretical bug"
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
       

    def test_create_feedback_anoun(self):
      
        data={
            "title":"for this type of bug",
            "description":" fix this bug ro you know this is cretical bug"
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
       

    def test_create_feedback_with_badword(self):
        self.client.force_authenticate(user=self.user)
        data={
            "title":"for this type of  land pussy bug",
            
            "description":" fix this bug ro you know this is cretical bug"
        }
        res=self.client.post(self.url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
       