from django.contrib import admin
from django.urls import path ,include
from django.conf.urls.static import static
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


v1_urls_patterns=[
    
    path("auth/",include('apps.account.api.urls')),
    path("Profile/",include('apps.Profile.api.urls')),
    path("post/",include("apps.post.api.urls")),
    path("notification/",include("apps.notification.api.urls")),
    path('feed/',include('apps.Feed.api.urls')),
    path("project-groupe/",include('apps.Chats.api.urls'),),
    path('Feedback/',include('apps.Feedback.api.urls')),
    path('safety/',include('apps.safety.api.urls'))

    
]

v2_urls_patterns=[
    
    
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((v1_urls_patterns, 'v1'))),

    path('silk/', include('silk.urls', namespace='silk')),
    path("api/schema/",SpectacularAPIView.as_view(),name="schema",),
    path("api/docs/",SpectacularSwaggerView.as_view(url_name="schema"),name="swagger-ui",),
    path("api/redoc/",SpectacularRedocView.as_view(url_name="schema"),name="redoc",),
    
]+debug_toolbar_urls()
