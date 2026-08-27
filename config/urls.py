from django.contrib import admin
from django.urls import path ,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/auth/",include('apps.account.api.urls')),
    path("api/v1/Profile/",include('apps.Profile.api.urls')),
    path("api/v1/Room/",include("apps.rooms.api.urls")),
    path("api/v1/post/",include("apps.post.api.urls")),
    path("api/v1/notification/",include("apps.notification.api.urls")),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/v1/feed/',include('apps.Feed.api.urls'))
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)