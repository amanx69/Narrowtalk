from django.urls import path
from .views import SignUp,VerifyEmail,LoginView

urlpatterns = [
    path("SignUp/",SignUp.as_view(),name="Signup"),
    path("verify-email/<str:token>/",VerifyEmail.as_view(),name="email-verify"),
    path("Login/",LoginView.as_view(),name="Login")
    
    
]
