from django.urls import path
from.views import ProfileView,ProflieLikeView,GetOtherUserProfile

urlpatterns = [
    path("me/",ProfileView.as_view(),name='user_profile'),
    path('profleLike/<uuid:Profile_id>/like/',ProflieLikeView.as_view(),name='profile-like'),
    path('other_profile/<uuid:user_id>/',GetOtherUserProfile.as_view(),name="get_profile")
]
