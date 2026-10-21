from django.urls import path
from .views import CreateFeedbackView

urlpatterns = [
    path('feedback/',CreateFeedbackView.as_view(),name='feedback')
]
