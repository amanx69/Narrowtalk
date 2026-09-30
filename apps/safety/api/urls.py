from .views import BlockUser ,ReportCreateView
from django.urls import path


urlpatterns = [
    path("block-user/<uuid:user_id>",BlockUser.as_view(),name='block_user'),
    path('report/', ReportCreateView.as_view(), name='create_report'),
]
