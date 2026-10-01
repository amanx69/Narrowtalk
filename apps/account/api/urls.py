from django.urls import path
from .views import (SignUp,
                    VerifyEmail,LoginView ,
                    ResetPasswordView,
                    SendForgetPassworEmaildView,
                    LogoutView ,
                    ResendVerifyEmailView, 
                    VerifyResetPasswordOtpView,
                    GoogleLoginAuthView
                    
)
urlpatterns = [
    path("Signup/",SignUp.as_view(),name="Signup"),
    path("Login/",LoginView.as_view(),name="Login"),
    path("verify-email/",VerifyEmail.as_view(),name="email-verify"),
    path("resend-verify-email/",ResendVerifyEmailView.as_view(),name="resend-verify-email"),
    path("verify-otp-reset-password/",VerifyResetPasswordOtpView.as_view(),name="verify-otp-reset-password"),
    path("reset-password/",ResetPasswordView.as_view(),name="reset-password"),
    path("google/", GoogleLoginAuthView.as_view(), name="google-login"),
    path("send-reset-email/",SendForgetPassworEmaildView.as_view(),name="send-reset-email-forgetpassword"),
    path("logout/",LogoutView.as_view(),name="logout"),

]
