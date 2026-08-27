from django.urls import path
from .views import(
     CommentProjectView,
     LikeProjectView,
     SaveProjectView ,
     ProjectViewTrackView,
     FeedView,
     HomeFeedView,
    TrandingProjectView
     
)

urlpatterns = [
    path('projects/<uuid:project_id>/like/', LikeProjectView.as_view(), name='project-like'),
    path('projects/<uuid:project_id>/save/', SaveProjectView.as_view(), name='project-save'),
    path('projects/<uuid:project_id>/comment/', CommentProjectView.as_view(), name='project-comment'),
    path('projects/<uuid:project_id>/view/', ProjectViewTrackView.as_view(), name='project-view'),
    path("project/Feed/",FeedView.as_view(),name="feed_view"),
    path('project/home_feed/',HomeFeedView.as_view(),name="home_feed"),
    path('project/best_project/',TrandingProjectView.as_view(),name="home_feed")
]