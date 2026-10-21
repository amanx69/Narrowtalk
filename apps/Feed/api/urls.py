from django.urls import path
from .views import(
     CommentProjectView,
     LikeProjectView,
     SaveProjectView ,
     ProjectViewTrackView,
     FeedView,
     HomeFeedView,
    TrandingProjectView,
    DeleteComment,
    ProjectSaveListApiView,
     
)

urlpatterns = [
    path('projects/<uuid:project_id>/like/', LikeProjectView.as_view(), name='project-like'),
    path('projects/<uuid:project_id>/save/', SaveProjectView.as_view(), name='project-save'),
    path("projects/saveproject/",ProjectSaveListApiView.as_view(),name="save-project-list"),
    path('projects/<uuid:project_id>/comment/', CommentProjectView.as_view(), name='project-comment'),
    path('project/<uuid:project_id>/deleteComment/<uuid:comment_id>/',DeleteComment.as_view(),name='deleted_comment'),
    path('projects/<uuid:project_id>/view/', ProjectViewTrackView.as_view(), name='project-view'),
    path("project/Feed/",FeedView.as_view(),name="feed_view"),
    path('project/home_feed/',HomeFeedView.as_view(),name="home_feed"),
    path('project/best_project/',TrandingProjectView.as_view(),name="home_feed")
]