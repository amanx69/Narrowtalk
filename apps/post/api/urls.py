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
    UserJoinProjectDetiles,
    RemoveMemberView

)
from .view.join_request import (
   
    AcceptJoinRequest,
    RejectJoinRequest,
    SendRequestForJoinProject,
    CurrentUserProjectNamesAPIView,
    CurrentUserPendingRequestsListAPIView,
    CurrentUserPendingRequestDetailAPIView,
    CurrentUserSentRequestsListAPIView,
    CurrentUserSentRequestDetailAPIView
)
from .view.projectview import UpdateProjectIscompleated, TransferProjectOwnershipView

router = DefaultRouter()
router.register("post", ProjectView, basename="post_urls")

urlpatterns = router.urls

urlpatterns += [
    path("apply_appliction/<uuid:roleNeed_id>/", ApplictionView.as_view(), name="appliction"),
    path("withdraw_appliction/<uuid:appliction_id>/", WithdrawAppliction.as_view(), name="withdraw_app"),
    path("accpect_appliction/<uuid:appliction_id>/", AccpectAppliction.as_view(), name="accpect_app"),
    path("reject_appliction/<uuid:appliction_id>/", RejectAppliction.as_view(), name="rejected_app"),
    path("leave_project/<uuid:project_id>/", LeaveProjectView.as_view(), name="leave_project"),
    path("remove-member/<uuid:project_id>/<uuid:user_id>/",RemoveMemberView.as_view(),name="remove_member"),
    path('role/appliction/pending/<uuid:role_id>/',RoleApplictionPendingListView.as_view(),name='pending_appliction'),
    path('role/appliction/accpect/<uuid:role_id>/',RoleApplictionAccpectedListView.as_view(),name='accpect_appliction'),
    path('role/appliction/reject/<uuid:role_id>/',RoleApplictionRejectedListView.as_view(),name='reject_appliction'),
    path('role/appliction/detile/<uuid:appliction_id>/',SingleApplictionDetils.as_view(),name="getsingle-appliction"),
    path('applied/appliction/all/',AppliedUserApplicationDetailView.as_view(),name="applied_userappliction_list"),
    path('applied/appliction/detile/<uuid:application_id>/',AppliedUserApplicationDetailView.as_view(),name="applied_userappliction_detail"),
    path('applied/appliction/accpeted/',AppliedUserAccpetedApplictionView.as_view(),name="applied_user_accpeted_appliction"),
    path('applied/joinproject/',UserJoinProjectDetiles.as_view(),name="join_project_list"),
    
    #send request urls
    path("request/send-join-request/",SendRequestForJoinProject.as_view(),name="send_request"),
    path("request/accpect_request/<uuid:request_id>/",AcceptJoinRequest.as_view(),name="accpect_join_request"),
    path("request/reject_request/<uuid:request_id>/",RejectJoinRequest.as_view(),name="reject_join_request"),
    path("request/current-user-projects/", CurrentUserProjectNamesAPIView.as_view(), name="current_user_project_names"),
    
    # pending requests received by current user
    path("request/pending-list/", CurrentUserPendingRequestsListAPIView.as_view(), name="pending_requests_list"),
    path("request/pending-detail/<uuid:pk>/", CurrentUserPendingRequestDetailAPIView.as_view(), name="pending_request_detail"),
    
    # sent requests by current user (owner)
    path("request/sent-list/", CurrentUserSentRequestsListAPIView.as_view(), name="sent_requests_list"),
    path("request/sent-detail/<uuid:pk>/", CurrentUserSentRequestDetailAPIView.as_view(), name="sent_request_detail"),
    
    # mark project completed
    path("project/complete/<uuid:project_id>/", UpdateProjectIscompleated.as_view(), name="complete_project"),
    path("project/transfer-ownership/<uuid:project_id>/", TransferProjectOwnershipView.as_view(), name="transfer_project_ownership"),
]