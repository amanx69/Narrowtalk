from rest_framework.generics import CreateAPIView
from rest_framework import status
from .serializers import FeedBackSerializer
from rest_framework.permissions import IsAuthenticated
from  core.throttling import FeedbackThrottle

class CreateFeedbackView(CreateAPIView):
    serializer_class=FeedBackSerializer
    throttle_classes=[FeedbackThrottle]
    permission_classes=[IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)