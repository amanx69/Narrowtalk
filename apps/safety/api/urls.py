from .views import BlockUser ,ReportCreateView
from django.urls import path


urlpatterns = [
    path("block-user/<uuid:user_id>", BlockUser.as_view(), name='block_user'),
    path("block-user/<uuid:user_id>/", BlockUser.as_view(), name='block_user_slash'),
    path('report/', ReportCreateView.as_view(), name='create_report'),
    path('report', ReportCreateView.as_view(), name='create_report_no_slash'),
]
