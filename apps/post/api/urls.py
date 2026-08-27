from rest_framework.routers import DefaultRouter
from django.urls import path 
from .views import (
    ProjectView,
    ApplictionView,
    WithdrawAppliction,
    AccpectAppliction,
    RejectAppliction,
    LeaveProjectView,
    RoleApplictionAccpectedListView,
    RoleApplictionPendingListView,
    RoleApplictionRejectedListView,
    SingleApplictionDetils,
    AppliedUserAccpetedApplictionView,
    AppliedUserApplicationDetailView,
)

router = DefaultRouter()
router.register("post", ProjectView, basename="post_urls")

urlpatterns = router.urls

urlpatterns += [
    path("apply_appliction/<uuid:roleNeed_id>/", ApplictionView.as_view(), name="appliction"),
    path("withdraw_appliction/<uuid:appliction_id>/", WithdrawAppliction.as_view(), name="withdraw_app"),
    path("accpect_appliction/<uuid:appliction_id>/", AccpectAppliction.as_view(), name="accpect_app"),
    path("reject_appliction/<uuid:appliction_id>/", RejectAppliction.as_view(), name="rej_app"),
    path("leave_project/<uuid:project_id>/", LeaveProjectView.as_view(), name="leave_proj"),
    path('role/appliction/pending/<uuid:role_id>/',RoleApplictionPendingListView.as_view(),name='pending_appliction'),
    path('role/appliction/accpect/<uuid:role_id>/',RoleApplictionAccpectedListView.as_view(),name='pending_appliction'),
    path('role/appliction/reject/<uuid:role_id>/',RoleApplictionRejectedListView.as_view(),name='pending_appliction'),
    path('role/appliction/get/<uuid:appliction_id>/',SingleApplictionDetils.as_view(),name="getsingle-appliction"),
    path('applied/appliction/all/',AppliedUserApplicationDetailView.as_view(),name="applied_userappliction_list"),
    path('applied/appliction/<uuid:application_id>/',AppliedUserApplicationDetailView.as_view(),name="applied_userappliction_list"),
    path('applied/appliction/accpeted/',AppliedUserAccpetedApplictionView.as_view(),name="applied_user_accpeted_appliction"),

    
]