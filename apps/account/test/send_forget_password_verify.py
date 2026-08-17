from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model


User= get_user_model()


class sendForgetpassWordVerifyTest(APITestCase):
    
    def setUp(self):
        self.url= reverse('send-reset-email')
        self.user= User.objects.create_user(
            email="test@gmail.com",
            password="Test@1234"
        )
        
        
    def test_send_forget_email(self):
        data={
            "email":"test@gmail.com"
        }
        
        res=self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, (
            status.HTTP_200_OK))
        self.assertEqual(res.data["message"],"reset password email send")
        
    def test_send_empty_email(self):
        data={
            "email":""
        }
        
        res= self.client.post(self.url ,data=data)
        self.assertEqual(res.status_code, (status.HTTP_400_BAD_REQUEST))
        
        
    def  test_send_Not_found_email(self):
        data={
            "email":"notfound@gmail.com"
        }
        res= self.client.post(self.url,data=data)
        self.assertAlmostEqual(res.status_code, (status.HTTP_404_NOT_FOUND))
        self.assertEqual(res.data["message"],"user not found")
        
        
# """      
#     def test_rate_limite(self):
#         data= {
#             "email":"test@gmail.com"
#         }
        
#         for _ in range(5):
#             res = self.client.post(self.url, data=data)
#             self.assertIn(res.status_code, (
#                 status.HTTP_200_OK,
#                 status.HTTP_404_NOT_FOUND,
#                 status.HTTP_400_BAD_REQUEST,
#             ))
#             print(res.status_code)
            
#         res= self.client.post(self.url, data=data)
#         print(res.status_code)
#         self.assertEqual(res.status_code ,status.HTTP_403_FORBIDDEN)  """