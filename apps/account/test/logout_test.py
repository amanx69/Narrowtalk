
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
User=get_user_model()


class LogoutTestCase(APITestCase):
    def setUp(self):
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )
        
        
    def test_logout_success(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        res = self.client.post(self.logout_url, data={"refresh": str(refresh)})
        self.assertEqual(res.status_code, status.HTTP_205_RESET_CONTENT)
        
    def test_logout_without_authentication(self):
        res = self.client.post(self.logout_url, data={"refresh": "dummy_refresh_token"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
    def test_logout_with_invalid_token(self):
        
        refresh= RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        res= self.client.post(self.logout_url, data={"refresh": "invalid_refresh_token"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
       