from ..models import Project
from ..api.serializer import FeedSerializer
from rest_framework.response import Response


def GetFeedFunction():
    
    data= Project.objects.all()
    ser=FeedSerializer(data)
    return ser.data
    
    