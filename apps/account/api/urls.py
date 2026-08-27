from django.urls import path
from .views import SignUp,VerifyEmail,LoginView , ResetPasswordView,SendForgetPassworEmaildView,LogoutView

urlpatterns = [
    path("Signup/",SignUp.as_view(),name="Signup"),
    path("verify-email/<str:token>/",VerifyEmail.as_view(),name="email-verify"),
    path("Login/",LoginView.as_view(),name="Login"),
    path("reset-password/<str:token>/",ResetPasswordView.as_view(),name="reset-password"),
    path("send-reset-email/",SendForgetPassworEmaildView.as_view(),name="send-reset-email"),
    path("logout/",LogoutView.as_view(),name="logout"),

]
